"""Boundary checks for the diagnostic; this does not establish live Lua API parity."""
import json
from pathlib import Path
import unittest
import tempfile
from lupa.lua51 import LuaRuntime
from frontier_discovery import ui_readback, liverpool_checkpoint, defer_autosave_source, SCANNER, QUOTE_BRIDGE, sha

FIXTURE = '''
output={};print=function(s)output[#output+1]=s end
function rows(values)local indexed={};for _,r in ipairs(values)do indexed[r.Index]=r end;return setmetatable(indexed,{__call=function()local n=0;return function()n=n+1;return values[n]end end})end
local district={HasDistrict=function()return false end}
local treasury={GetGoldBalance=function()return 50 end,GetGoldYield=function()return 10 end,GetTotalMaintenance=function()return 2 end}
gold={GetPlotPurchaseCost=function(self,index)assert(index==31);return 145 end}
city={GetID=function()return 42 end,GetName=function()return 'Fixture' end,GetX=function()return 0 end,GetY=function()return 0 end,GetDistricts=function()return district end,GetGold=function()return gold end}
-- Native Members yields the iteration key and object separately.
local cities={Members=function()local done=false;return function()if not done then done=true;return 0,city end end end}
player={IsAlive=function()return true end,IsMajor=function()return true end,IsHuman=function()return false end,GetTreasury=function()return treasury end,GetCities=function()return cities end}
Players={[1]=player};PlayersVisibility={[1]={IsRevealed=function()return true end}}
local function plot(index,owner,district)return {GetIndex=function()return index end,GetX=function()return index end,GetY=function()return 0 end,GetOwner=function()return owner end,GetDistrictType=function()return district end,GetResourceType=function()return -1 end,CanHaveDistrict=function()return true end,GetRiverCrossingCount=function()return 0 end}end
site=plot(31,-1,-1);host=plot(2,1,0)
Map={GetGridSize=function()return 74,46 end,GetPlot=function()return host end,GetAdjacentPlots=function()return {host}end}
GameInfo={Districts=rows({{Index=0,DistrictType='DISTRICT_CITY_CENTER'}}),Resources={}}
CSC_Adjacency={Initialize=function()end,PlotsInBand=function()return {site}end,HasTag=function()return false end,ResourceVisible=function()return true end}
profile={key='BAKERS',district={Index=36},customers={[0]={}},base='BASE',producers={}}
CSC_AI_QuarterPlacement={StageTwoProfiles=function()return {profile}end,ReadSuppliers=function()return {base={{plot=1,working=true,ready=true}},specialty={}}end}
Game={GetCurrentGameTurn=function()return 200 end}
'''


class Discovery(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime()
        self.lua.execute(FIXTURE)
        self.script = Path(__file__).with_name('frontier_site_survey.lua').read_text()

    def sample(self, change=''):
        self.lua.execute(change)
        self.lua.execute(self.script)
        lines = self.lua.globals().output
        return json.loads(lines[len(lines)].split('=', 1)[1])

    def test_known_supply_customer_and_economy(self):
        data = self.sample()
        self.assertEqual(data['sites'][0]['quote'], 145)
        self.assertTrue(data['sites'][0]['hosts'][0]['stageTwo'])
        self.assertTrue(data['sites'][0]['quoteAvailable'])
        self.assertEqual(data['players'][0]['treasuryGold'], 50)
        self.assertEqual(data['players'][0]['goldYield'], 10)

    def test_owned_comparison_requires_explicit_city_and_correct_purchase_city(self):
        for enabled,city_id in ((False,42),(True,42),(True,99)):
            with self.subTest(enabled=enabled,city=city_id):
                self.setUp()
                data=self.sample('site.GetOwner=function()return 1 end\n'
                    +'Cities={GetPlotPurchaseCity=function()return {GetID=function()return '+str(city_id)+' end}end}\n'
                    +('CSC_FRONTIER_COMPARISON={[1]={[42]=true}}' if enabled else ''))
                accepted=enabled and city_id==42
                self.assertEqual(len(data['sites']),int(accepted))
                self.assertEqual(data['players'][0]['frontierPairs'],0)
                self.assertEqual(data['players'][0]['ownedComparisonPairs'],int(accepted))
                if accepted:self.assertTrue(data['sites'][0]['ownedComparison'])

    def test_missing_quote_is_explicit(self):
        row = self.sample('city.GetGold=nil')['sites'][0]
        self.assertFalse(row['quoteAvailable'])
        self.assertNotIn('quote', row)
        self.assertIn('missing method', row['quoteError'])

    def test_nonpositive_quote_is_retained_as_a_lead(self):
        row = self.sample('gold.GetPlotPurchaseCost=function()return -1 end')['sites'][0]
        self.assertTrue(row['quoteAvailable'])
        self.assertEqual(row['quote'], -1)

    def test_no_base_is_not_promoted_to_known_supply(self):
        data = self.sample('CSC_AI_QuarterPlacement.ReadSuppliers=function()return {base={},specialty={}}end')
        self.assertEqual(data['sites'], [])
        self.assertEqual(data['players'][0]['frontierPairs'], 1)

    def test_foreign_or_unrevealed_site_is_not_frontier(self):
        for change in ('site.GetOwner=function()return 2 end',
            'PlayersVisibility[1].IsRevealed=function()return false end'):
            self.setUp()
            data = self.sample(change)
            self.assertEqual(data['sites'], [])
            self.assertEqual(data['players'][0]['frontierPairs'], 0)

    def test_ui_pairs_are_deduplicated_and_joined(self):
        class Controller:
            def cmd(self, code, context, label):
                assert context == 'PlotInfo' and 'CanStartCommand' in code
                return ('O\0CSC_FRONTIER_UI_QUOTE\t1\t42\t31\t145\ttrue\r\n'
                    'O\0CSC_FRONTIER_UI_ECONOMY\t1\t150\t12\t2\r\n'
                    'O\0CSC_FRONTIER_UI_END\t200\t1\t1\t0\r\n')
        state=dict(turn=200,players=[dict(player=1)],sites=[dict(player=1,city=42,plot=31)],
            supplierLeads=[dict(player=1,city=42,plot=31)])
        parent=Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=parent,prefix='.discovery-test-') as folder:
            assert Path(folder).resolve().parent==parent
            ui_readback(Controller(),Path(folder),state)
        self.assertEqual(state['sites'][0]['ui'],dict(quote=145.0,uiCanStartAtBoundary=True))
        self.assertEqual(state['supplierLeads'][0]['ui'],state['sites'][0]['ui'])
        self.assertEqual(state['uiEconomy'][0]['treasuryGold'],150)

    def test_future_projection_uses_one_alternative(self):
        data=self.sample('''
GameInfo.Districts=rows({{Index=0,DistrictType='DISTRICT_CITY_CENTER'},
 {Index=4,DistrictType='DISTRICT_HARBOR'},{Index=5,DistrictType='DISTRICT_COMMERCIAL_HUB'}})
host.GetDistrictType=function()return -1 end
city.GetOwner=function()return 1 end
Cities={GetPlotPurchaseCity=function()return city end}
CSC_Adjacency.HasTag=function(tag,kind)return tag=='CLASS_CSC_BAKERS_SALES' end
CSC_AI_FutureDistrictTypes=function()return {[4]=true,[5]=true}end
CSC_AI_QuarterAdjacencyValue=function(kind,site,city,pid,omit,future)
 local gold=future=='DISTRICT_COMMERCIAL_HUB' and 3 or future=='DISTRICT_HARBOR' and 2 or 1
 return {production=1,gold=gold,total=1+gold,current={production=1,gold=1},details={}}
end
''')
        row=data['sites'][0]
        self.assertTrue(data['modelAvailable'])
        self.assertEqual(len(row['futureForecasts']),2)
        self.assertEqual(row['bestFutureType'],'DISTRICT_COMMERCIAL_HUB')
        self.assertEqual(row['maximumProjection']['total'],4)

    def test_buyer_matrix_requires_one_readable_quote_per_current_city(self):
        class Controller:
            def __init__(self,quotes):self.quotes=quotes
            def cmd(self,code,context,label):
                return ('CSC_FRONTIER_UI_ECONOMY\t1\t150\t12\t2\n'
                    'CSC_FRONTIER_UI_CITY\t1\t42\t2\t1\t4\n'
                    'CSC_FRONTIER_UI_END\t202\t0\t1\t1\n'+self.quotes)
        for quotes,valid in [('CSC_COMPARISON_BUYER_QUOTE\t1\t31\t42\t145',True),('',False),
                ('CSC_COMPARISON_BUYER_QUOTE\t1\t31\t42\tnil',False),
                ('CSC_COMPARISON_BUYER_QUOTE\t1\t31\t99\t145',False),
                ('CSC_COMPARISON_BUYER_QUOTE\t1\t31\t42\t145\nCSC_COMPARISON_BUYER_QUOTE\t1\t31\t42\t145',False)]:
            with self.subTest(quotes=quotes),tempfile.TemporaryDirectory() as folder:
                state=dict(turn=202,players=[dict(player=1)],sites=[],supplierLeads=[],
                    cityStates=[dict(player=1,city=42)],buyerPlots=[dict(player=1,plot=31)])
                if valid:ui_readback(Controller(quotes),Path(folder),state)
                else:
                    with self.assertRaisesRegex(AssertionError,'Incomplete all-city'):
                        ui_readback(Controller(quotes),Path(folder),state)

    def test_liverpool_source_requires_inactive_checkpoint_and_same_policy(self):
        # Guard the exact observed autosave failure: origin metadata and a
        # plausible filename never substitute for verified inactive human0.
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);run=root/'run';run.mkdir()
            home=root/'home';native=home/'Saves/Single/source.Civ6Save'
            native.parent.mkdir(parents=True);native.write_bytes(b'CIV6-test')
            archive=run/'source.Civ6Save';archive.write_bytes(native.read_bytes())
            policy=root/'policy'
            paths=(SCANNER,Path('Lua_UI/AI/CSC_AI_BakersGameplay.lua'),QUOTE_BRIDGE,
                Path('Lua_UI/AI/CSC_AI_QuarterPlacement.lua'),Path('Lua_UI/AI/CSC_AI_DistrictBridge.lua'))
            for p in paths:
                (policy/p).parent.mkdir(parents=True,exist_ok=True);(policy/p).write_bytes(b'unchanged')
            def write(name,value):(run/name).write_text(json.dumps(value),encoding='utf-8')
            write('complete.json',dict(verified=True));write('session-closed.json',dict(verified=True))
            write('liverpool-source.json',dict(verified=True,source_world_sha256='world',
                native_fresh_comparison_verified=False,main_policy_sha256={str(p):sha(policy/p)for p in paths}))
            phase=dict(turn=25,active=False,local_player=0,player0_human=True)
            checkpoint=dict(verified=True,turn=25,save_complete_event=True,native_phase_unchanged=True,
                before=phase,after=phase,native_save=str(native),archive=str(archive),sha256=sha(native))
            write('checkpoint.json',checkpoint)
            self.assertEqual(liverpool_checkpoint(run,home,'world',policy)['turn'],25)
            with self.assertRaisesRegex(AssertionError,'not an autosave descriptor'):
                liverpool_checkpoint(run/'liverpool-source.json',home,'world',policy)
            checkpoint['after']=dict(phase,turn=27,player0_human=False);write('checkpoint.json',checkpoint)
            with self.assertRaises(AssertionError):liverpool_checkpoint(run,home,'world',policy)
            checkpoint['after']=phase;write('checkpoint.json',checkpoint)
            (policy/SCANNER).write_bytes(b'changed')
            with self.assertRaises(AssertionError):liverpool_checkpoint(run,home,'world',policy)

    def test_raw_deferral_source_is_provenance_only_and_rejects_policy_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);run=root/'source';run.mkdir()
            parent=root/'failed-parent';parent.mkdir()
            (parent/'session-closed.json').write_text(json.dumps(dict(verified=True)))
            (parent/'failure.json').write_text(json.dumps(dict(error=
                'Native checkpoint file did not settle; never resend blindly')))
            home=root/'home';native=home/'Saves/Single/source.Civ6Save'
            native.parent.mkdir(parents=True);native.write_bytes(b'CIV6-provenance-only')
            archive=run/'source.Civ6Save';archive.write_bytes(native.read_bytes())
            policy=root/'policy'
            paths=(SCANNER,Path('Lua_UI/AI/CSC_AI_BakersGameplay.lua'),QUOTE_BRIDGE,
                Path('Lua_UI/AI/CSC_AI_QuarterPlacement.lua'),Path('Lua_UI/AI/CSC_AI_DistrictBridge.lua'))
            for p in paths:
                (policy/p).parent.mkdir(parents=True,exist_ok=True);(policy/p).write_bytes(b'unchanged')
            meta=dict(verified_file_copy=True,qualified_inactive_source=False,
                requires_cold_qualification=True,expected_turn=30,parent=str(parent),
                parent_source_sha256='world',native_save=str(native),archive=str(archive),
                sha256=sha(native),main_policy_sha256={str(p):sha(policy/p)for p in paths})
            (run/'source.json').write_text(json.dumps(meta))
            result=defer_autosave_source(run,home,'world',policy)
            self.assertTrue(result['requires_cold_qualification'])
            self.assertEqual(result['turn'],30)
            (policy/SCANNER).write_bytes(b'changed')
            with self.assertRaises(AssertionError):defer_autosave_source(run,home,'world',policy)


if __name__ == '__main__':
    unittest.main()
