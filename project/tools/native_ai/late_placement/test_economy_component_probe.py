"""Component inspection retains original facts and isolates a read-only variant."""
import json
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
from economy_component_probe import targets


class ComponentProbe(unittest.TestCase):
    def fixture(self,improvement):
        vm=LuaRuntime()
        vm.execute('''
logs={};print=function(s)logs[#logs+1]=s end
Game={GetCurrentGameTurn=function()return 155 end}
site={horizon=50,quarterReady=10,adjacency=3,direct={
 {id='displaced:YIELD_FOOD',yield='YIELD_FOOD',amount=-2},
 {id='YIELD_PRODUCTION',yield='YIELD_PRODUCTION',amount=1}},seconds={{unlock=math.huge}}}
local city={GetPopulation=function()return 2 end}
Players={[4]={IsHuman=function()return false end,GetCities=function()return{FindID=function()return city end}end}}
ExposedMembers={CSC_Adjacency={}}
local snapshot={cities={[393221]={production=2.4}},PlotFacts=function()return{workers=1}end,
 Geometry=function()return{upper=3}end,Site=function()return site end,Price=function()end}
CSC_AI_EconomyAdapters={Snapshot=function()return snapshot end,PlacementValue=function(q)return q.valueQ8 end}
CSC_AI_QuarterPlacement={StageTwoProfiles=function()return{{key='BAKERS'}}end}
CSC_AI_EconomyModel={Forecast=function(s)
 local total=0;for _,v in ipairs(s.direct)do total=total+v.amount end
 return{valueQ8=total*256,streams=s.direct}
end}
CSC_COMPONENT_TARGETS={{player=4,city=393221,plot=2992,key='BAKERS'}}
''')
        vm.execute('''Map={GetPlotByIndex=function()return{
 GetImprovementType=function()return %d end,GetTerrainType=function()return 1 end,
 GetFeatureType=function()return -1 end,GetResourceType=function()return -1 end,
 GetOwner=function()return 4 end}end}'''%improvement)
        vm.execute(Path(__file__).with_name('economy_component_probe.lua').read_text())
        raw=[s for s in vm.globals().logs.values()if s.startswith('CSC_ECONOMY_COMPONENT=')]
        return vm,json.loads(raw[0].split('=',1)[1])

    def test_unimproved_counterfactual_preserves_source_facts_and_horizon(self):
        vm,row=self.fixture(-1)
        self.assertEqual(row['quote']['valueQ8'],-256)
        self.assertEqual(row['withoutUnimprovedFootprint']['valueQ8'],256)
        self.assertEqual(row['site']['horizon'],50)
        self.assertEqual(row['site']['seconds'][0]['unlock'],'Infinity')
        self.assertEqual(vm.eval('#site.direct'),2)
        self.assertTrue(row['diagnosticOnly'])

    def test_improved_supplier_loss_is_not_removed_by_the_variant(self):
        _,row=self.fixture(0)
        self.assertNotIn('withoutUnimprovedFootprint',row)
        self.assertEqual(row['quote']['valueQ8'],-256)

    def test_targets_are_explicit_original_ai_and_bounded(self):
        self.assertEqual(targets([['4','393221','2992','BAKERS']])[0]['plot'],2992)
        with self.assertRaises(RuntimeError):targets([['0','393221','2992','BAKERS']])
        with self.assertRaises(RuntimeError):targets([['4','393221','2992','BAKERS']]*9)


if __name__=='__main__':unittest.main()
