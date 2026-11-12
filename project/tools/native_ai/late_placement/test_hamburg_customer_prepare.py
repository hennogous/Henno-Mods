"""Check that common diagnostic placement protects source facts and never retries."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

CODE=Path(__file__).with_name('hamburg_customer_prepare.lua').read_text()
FIXTURE=r'''
writes=0;improvement=8;feature=3;created=false;protected=false;legal=true;queued='BUILDING_COAL_POWER_PLANT'
changeQueue=false;CSC_HAMBURG_CUSTOMER_PREPARE_PLOT=1083
print=function()end
Game={GetCurrentGameTurn=function()return 208 end,GetLocalPlayer=function()return 0 end}
AutoplayManager={IsActive=function()return false end}
Players={[0]={IsHuman=function()return true end},[3]={IsHuman=function()return false end,
 GetTreasury=function()return {GetGoldBalance=function()return 100 end}end}}
local quarter={Index=37,Hash=37};local harbor={Index=4,Hash=4}
GameInfo={Districts={DISTRICT_HARBOR=harbor,DISTRICT_ENCAMPMENT={Index=3}},Resources={RESOURCE_SHEEP={Index=7}},
 Improvements={IMPROVEMENT_LUMBER_MILL={Index=8}},Features={[3]={FeatureType='FEATURE_FOREST'}}}
local function plot(index,x,y)
 return {GetIndex=function()return index end,GetX=function()return x end,GetY=function()return y end,
 GetOwner=function()return 3 end,GetResourceType=function()return index==1084 and 7 or -1 end,
 GetResourceCount=function()return index==1084 and 1 or 0 end,
 GetDistrictType=function()return index==1083 and created and 37 or -1 end,
 GetImprovementType=function()return index==1083 and improvement or -1 end,
 GetFeatureType=function()return index==1083 and feature or -1 end,GetTerrainType=function()return 3 end}
end
local plots={[1083]=plot(1083,47,14),[1084]=plot(1084,48,14),
 [1082]=plot(1082,46,14),[1156]=plot(1156,46,15)}
Map={GetPlotByIndex=function(i)return plots[i]end,GetPlotDistance=function()return 1 end}
Cities={GetPlotPurchaseCity=function()return {GetID=function()return 393221 end}end}
local result={GetType=function()return 37 end,GetX=function()return 47 end,GetY=function()return 14 end,
 IsComplete=function()return true end,IsPillaged=function()return false end,GetID=function()return 99 end}
local districts={HasDistrict=function(_,kind)return kind==37 and created end,
 GetNumDistricts=function()return created and 1 or 0 end,GetDistrictByIndex=function()return result end}
local queue={CurrentlyBuilding=function()return queued end,CreateIncompleteDistrict=function(_,kind,index,progress)
 assert(kind==37 and index==1083 and progress==100);writes=writes+1;created=true
 if changeQueue then queued='UNIT_BUILDER'end end}
local city={GetName=function()return 'LOC_CITY_NAME_HAMBURG'end,GetPopulation=function()return 7 end,
 GetBuildQueue=function()return queue end,GetDistricts=function()return districts end}
CityManager={GetCity=function()return city end}
CSC_Adjacency={Initialize=function()end}
CSC_AI_QuarterPlacement={StageTwoProfiles=function()return {{key='TAILORS',district=quarter,customers={[4]={}}}}end,
 ReadSuppliers=function()return {base={{plot=1084,ready=true}}}end,
 MaterialDeductions=function()return protected and {{plot=1083}}or {}end}
ExposedMembers={CSC_Adjacency={GetLegalDistrictTargets=function(_,_,hash)
 if hash==37 then return legal and {1083}or {}end;return {1082,1156}end}}
ImprovementBuilder={SetImprovementType=function(p,kind,owner)
 assert(p==plots[1083]and kind==-1 and owner==3);writes=writes+1;improvement=kind end}
TerrainBuilder={SetFeatureType=function(p,kind)
 assert(p==plots[1083]and kind==-1);writes=writes+1;feature=kind end}
'''


class CommonQuarterPreparation(unittest.TestCase):
    def test_empty_site_needs_only_the_declared_quarter_creation(self):
        vm=LuaRuntime();vm.execute(FIXTURE+'improvement=-1;feature=-1');vm.execute(CODE)
        self.assertEqual(vm.globals().writes,1);self.assertTrue(vm.globals().created)
        self.assertEqual(vm.globals().queued,'BUILDING_COAL_POWER_PLANT')

    def test_declared_lumber_mill_conversion_and_duplicate_refusal(self):
        vm=LuaRuntime();vm.execute(FIXTURE);vm.execute(CODE)
        self.assertEqual((vm.globals().writes,vm.globals().improvement,vm.globals().feature),(3,-1,-1))
        with self.assertRaises(Exception):vm.execute(CODE)
        self.assertEqual(vm.globals().writes,3)

    def test_protected_or_illegal_source_refuses_all_writes(self):
        for changed in('protected=true','legal=false','improvement=9','queued="DISTRICT_ENCAMPMENT"'):
            vm=LuaRuntime();vm.execute(FIXTURE+changed)
            with self.assertRaises(Exception):vm.execute(CODE)
            self.assertEqual(vm.globals().writes,0)

    def test_unexpected_queue_change_leaves_failed_fixture_nonretryable(self):
        vm=LuaRuntime();vm.execute(FIXTURE+'changeQueue=true')
        with self.assertRaises(Exception):vm.execute(CODE)
        self.assertIsNotNone(vm.globals().CSC_HAMBURG_CUSTOMER_PREPARE_STATE)
        with self.assertRaises(Exception):vm.execute(CODE)
        self.assertEqual(vm.globals().writes,3)


if __name__=='__main__':unittest.main()
