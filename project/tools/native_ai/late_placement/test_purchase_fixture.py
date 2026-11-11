"""Qualify buyer/cash ambiguities before a source-identified live replay."""
import json
from pathlib import Path
import tempfile
import unittest
from lupa.lua51 import LuaRuntime

from nicopolis_replay import CASES, WATCHER, qualify_purchase, ablate_frontier_offer
from driver import lua

FIXTURE = '''
prices={85,130,-1};bank=719;owner=-1;output={}
print=function(...)local args={...};for i=1,select('#',...)do args[i]=tostring(args[i])end
 output[#output+1]=table.concat(args,'\t')end
local ids={589829,524292,393216}
local cities={}
for i,id in ipairs(ids)do
 cities[i]={GetID=function()return id end,GetName=function()return i==1 and 'LOC_CITY_NAME_SZEGED' or 'Other' end,
  GetGold=function()return {GetPlotPurchaseCost=function(_,target)assert(target==1365);return prices[i]end}end,
  GetBuildQueue=function()return {CanProduce=function()return true end,CurrentlyBuilding=function()return 'UNIT_SETTLER'end}end,
  GetDistricts=function()return {GetNumAllowedDistrictsRequiringPopulation=function()return 2 end,
   GetNumZonedDistrictsRequiringPopulation=function()return 2 end}end}
end
local player={IsHuman=function()return false end,
 GetTreasury=function()return {GetGoldBalance=function()return bank end}end,
 GetCities=function()return {Members=function()local i=0;return function()i=i+1;if cities[i]then return i,cities[i]end end end}end}
Players={[2]=player};CityManager={GetCity=function(pid,id)assert(pid==2 and id==589829);return cities[1]end}
Map={GetPlotByIndex=function(id)assert(id==1365);return {GetOwner=function()return owner end,GetDistrictType=function()return -1 end}end}
GameInfo={Districts={[37]={Hash=10037}}};Game={GetCurrentGameTurn=function()return 200 end}
'''


class Controller:
    def __init__(self, change=''):
        self.vm=LuaRuntime()
        self.vm.execute(FIXTURE+change)

    def cmd(self, code, state, label):
        assert state=='PlotInfo'
        self.vm.execute(code)
        return '\n'.join(self.vm.globals().output.values())


class Qualification(unittest.TestCase):
    def test_all_city_quotes_and_source_bank_are_recorded(self):
        with tempfile.TemporaryDirectory() as path:
            qualify_purchase(Controller(),Path(path),CASES['szeged'])
            record=json.loads((Path(path)/'source-purchase-qualification.json').read_text())
            self.assertTrue(record['verified'])
            self.assertEqual((record['cities_quoted'],record['quote'],record['treasuryGold']),(3,85,719))

    def test_cheaper_other_city_tie_shortfall_and_occupied_plot_fail_preflight(self):
        for change, message in [('prices[2]=80','proposing-city'),('prices[2]=85','tied'),
                ('bank=84','Treasury'),('owner=2','occupied')]:
            with self.subTest(change=change),tempfile.TemporaryDirectory() as path:
                with self.assertRaisesRegex(Exception,message):
                    qualify_purchase(Controller(change),Path(path),CASES['szeged'])
                self.assertFalse((Path(path)/'source-purchase-qualification.json').exists())

    def test_both_watchers_compile_with_their_exact_scope(self):
        vm=LuaRuntime()
        compile_lua=vm.eval('function(code)return assert(loadstring(code))end')
        for case in CASES.values():
            with self.subTest(case=case['profile']):
                compile_lua(WATCHER.replace('__SCOPE__',lua(case)).replace('__ENDPOINT__','208'))

    def test_ablation_changes_only_the_fixture_positive_candidate_condition(self):
        path=Path(__file__).resolve().parents[4]/'Civ Supply Chains/Lua_UI/AI/CSC_AI_AdjacencyScan.lua'
        source=path.read_bytes()
        changed=ablate_frontier_offer(source,CASES['szeged'])
        before=source.splitlines();after=changed.splitlines()
        differences=[(a,b)for a,b in zip(before,after)if a!=b]
        self.assertEqual(len(before),len(after))
        self.assertEqual(len(differences),1)
        self.assertIn(b'pid == 2 and city:GetID() == 589829 and district.Index == 37 and index == 1365',differences[0][1])
        LuaRuntime().eval('function(code)return assert(loadstring(code))end')(changed.decode('utf-8-sig'))

    def test_live_quote_bridge_rejects_ambiguous_buyer_without_reading_bank(self):
        controller=Controller()
        vm=controller.vm
        vm.execute("ExposedMembers={};Players[2].GetTreasury=function()error('No live cash veto')end")
        path=Path(__file__).resolve().parents[4]/'Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyUI.lua'
        vm.execute(path.read_text(encoding='utf-8-sig'))
        quote=vm.eval('function()return ExposedMembers.CSC_Adjacency.GetPlotPurchaseQuote(2,589829,1365)end')
        self.assertEqual(quote(),85)
        for change in ('prices[2]=85','prices[2]=80','prices[2]=nil','prices[1]=-1'):
            with self.subTest(change=change):
                vm.execute('prices={85,130,-1};'+change)
                self.assertIsNone(quote())


if __name__=='__main__':unittest.main()
