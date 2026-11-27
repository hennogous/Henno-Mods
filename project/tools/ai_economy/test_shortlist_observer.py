"""Exercise the live diagnostic against ranks deliberately hidden from its selector."""

from pathlib import Path
import sys
import unittest
from lupa.lua51 import LuaRuntime


OBSERVER = Path(__file__).resolve().parents[1]/"native_ai/late_placement/shortlist_observer.lua"
sys.path.insert(0, str(OBSERVER.parent))
from shortlist_results import analyze


class ShortlistObserver(unittest.TestCase):
    def setUp(self):
        self.vm = LuaRuntime()
        self.lines = []
        self.vm.globals().print = lambda *args: self.lines.append(" ".join(map(str, args)))
        self.vm.execute("""
            CSC_AI_EconomyAdapters={}
            Game={GetCurrentGameTurn=function() return turn end}
            GameInfo={Districts={[0]={}}}
            local visibility={IsVisible=function() return false end,IsRevealed=function() return false end}
            PlayersVisibility={[0]=visibility}
            local plot={GetX=function()return 0 end, GetY=function()return 0 end,
                GetIndex=function(p)return p.id end, GetOwner=function()return 0 end}
            Map={GetPlotByIndex=function()return plot end}
            local player={GetTreasury=function()return {GetGoldBalance=function()return 10 end} end}
            local city={GetID=function()return 0 end}
            local profile={key='TAILORS',district={Index=0}}
            function sample(t,hot,changed,protected)
                turn=t
                local s={id=0,player=player,DistrictCapacity=function()return {reason='ready'} end,
                    intentFootprints={[protected or -1]=true}}
                local e,attempts={},0
                visited={}
                for i=1,7 do
                    plot.id=i
                    local site={startingAdjacency=(changed==i and 4 or 3),baseCount=2,specialtyCount=1}
                    local decision=CSC_AI_EconomyAdapters.ShortlistObserver.site(s,city,plot,profile,site,{},0,nil)
                    if decision~=false then
                        attempts=attempts+1
                        visited[i]=true
                        if hot~=-1 then
                            e[#e+1]={economy=true,city=0,district=0,plot=i,finalQ8=(hot==i and 100 or 10-i),
                                customerLayout=(i==1 and {{plot=7}} or {})}
                        end
                    end
                end
                CSC_AI_EconomyAdapters.ShortlistObserver.finish(s,e)
                return attempts
            end
        """)
        self.vm.execute(OBSERVER.read_text(encoding="utf-8"))

    def scope(self, *args):
        self.vm.globals().sample(*args)
        row = next(line for line in reversed(self.lines) if line.startswith("CSC_SHORTLIST_SCOPE"))
        return {k: int(v) for k,v in (field.split("=") for field in row.split()[1:]) if v.isdigit()}

    def test_shadow_history_rotation_and_refresh(self):
        self.assertEqual(self.scope(2,0)["kept"],7)
        self.assertEqual(self.scope(3,7)["alternate"],1)
        # Seeing plot 7 win the full ranking does not promote it on the next turn.
        self.assertEqual(self.scope(4,7)["alternate"],1)
        self.assertEqual(self.scope(5,7,7)["alternate"],7)
        self.assertEqual(self.scope(6,7,7)["alternate"],7)
        self.assertEqual(self.scope(8,0)["cold"],1)
        self.assertEqual(self.scope(9,0)["kept"],3)

    def test_protection_and_periodic_refresh(self):
        self.scope(5,0)
        row = self.scope(6,7,0,7)
        self.assertEqual((row["alternate"],row["kept"]),(7,4))
        self.scope(7,0)
        row = self.scope(8,0)
        self.assertEqual((row["cold"],row["kept"]),(0,7))

    def test_live_cutoff_rescans_empty_groups_and_prices_prior_customer(self):
        self.vm.execute("CSC_AI_EconomyAdapters.ShortlistObserver=nil; CSC_LIVE_SHORTLIST=true; "
                        "CSC_AI_EconomyAdapters.SupportsSelectiveQuarterForecasts=true")
        self.vm.execute(OBSERVER.read_text(encoding="utf-8"))
        sample=self.vm.globals().sample
        self.assertEqual(sample(2,0),7)
        # Plot 7 was plot 1's customer. It wins now and remains in the next
        # pass's leaders even though that next turn has no changed sites.
        self.assertEqual(sample(3,7),4)
        self.assertTrue(self.vm.eval("visited[7]"))
        self.assertEqual(sample(4,-1),3)
        self.assertEqual(sample(5,7),7)
        sample(6,7,6,5)
        self.assertTrue(self.vm.eval("visited[5] and visited[6] and visited[7]"))
        self.assertEqual(sample(8,0),7)

    def test_report_reconciles_with_normal_publication(self):
        for turn, hot in ((2,0),(3,7),(4,0)):
            row = self.scope(turn,hot)
            self.lines.extend([
                f"CSC_AI_PROCESSING turn={turn} ok=1 published=1",
                f"CSC_AI_ECONOMY_PLAN turn={turn} player=0",
                f"CSC_AI_SPATIAL_BID turn={turn} player=0 city=0 district=0 "
                f"rank=1 plot={row['winner']} finalQ8={row['bid']}",
            ])
        total = analyze(self.lines,2,4)["groups"]["all"]
        self.assertEqual((total["calls"],total["skipped"],total["winners"],total["exact"]),(21,8,3,2))
        with self.assertRaisesRegex(AssertionError, "ranking"):
            analyze(self.lines[:-1],2,4)
