"""Guard the diagnostic's two declared resource edits and ordinary publication boundary."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
from washington_opportunity import PREPARE,RESTORE,stage


FIXTURE=r'''
resource=1;count=1;writes=0;owner=3;hidden=false;unknown=false;anotherBase=false;initialized=false
gold=45;population=4;queued='DISTRICT_CAMPUS';scope=1
print=function()end
Game={GetCurrentGameTurn=function()return 22 end,GetLocalPlayer=function()return 0 end}
AutoplayManager={IsActive=function()return false end}
Players={[0]={IsHuman=function()return true end},[3]={IsHuman=function()return false end,
 GetTreasury=function()return {GetGoldBalance=function()return gold end}end}}
city={GetName=function()return 'LOC_CITY_NAME_WASHINGTON'end,GetPopulation=function()return population end,
 GetDistricts=function()return {HasDistrict=function()return false end}end,
 GetBuildQueue=function()return {CurrentlyBuilding=function()return queued end}end}
CityManager={GetCity=function(pid,cid)assert(pid==3 and cid==65536);return city end}
local cattle={Index=1,ResourceType='RESOURCE_CATTLE'}
local wheat={Index=2,ResourceType='RESOURCE_WHEAT'}
GameInfo={Districts={DISTRICT_CSC_BAKERS_QUARTER={Index=36}},
 Resources=setmetatable({RESOURCE_CATTLE=cattle,[1]=cattle,[2]=wheat},{__call=function()
  local i=0;return function()i=i+1;return ({cattle,wheat})[i]end end})}
CSC_Adjacency={Initialize=function()initialized=true end,
 HasTag=function(tag,kind)assert(tag=='CLASS_CSC_BAKERS_BASE');return initialized and (kind=='RESOURCE_CATTLE'or kind=='RESOURCE_WHEAT')end,
 ResourceVisible=function(pid,index)assert(pid==3);return not hidden or index~=2 end}
PlayersVisibility={[3]={IsRevealed=function()return not unknown end}}
supplier={GetOwner=function()return owner end,GetResourceType=function()return resource end,
 GetResourceCount=function()return count end,GetImprovementType=function()return -1 end,
 GetDistrictType=function()return -1 end,GetTerrainType=function()return 2 end,
 GetFeatureType=function()return -1 end,GetRiverCrossingCount=function()return 0 end,
 GetX=function()return 56 end,GetY=function()return 10 end,GetIndex=function()return 796 end}
site={GetOwner=function()return 3 end,GetDistrictType=function()return -1 end,
 GetX=function()return 56 end,GetY=function()return 11 end}
local other={GetOwner=function()return -1 end,GetResourceType=function()return anotherBase and 1 or -1 end,
 GetImprovementType=function()return -1 end,GetIndex=function()return 869 end,
 GetX=function()return 55 end,GetY=function()return 11 end}
Map={GetPlotByIndex=function(i)assert(i==796 or i==870);return i==796 and supplier or site end,
 GetAdjacentPlots=function()return {supplier,other}end,GetPlotDistance=function()return 1 end}
Cities={GetPlotPurchaseCity=function(p)return {GetID=function()return p==supplier and 131073 or 65536 end}end}
ResourceBuilder={SetResourceType=function(p,r,n)assert(p==supplier);writes=writes+1;resource=r;count=n or 0 end}
CE_AIDistrictScoresStatus=function()return '{"version":1}'end
CE_AIDistrictDeclineReceipt=function()return '{"staged":'..scope..'}'end
CSC_AI_QuarterPlacement={StageTwoProfiles=function()return {{key='BAKERS'}}end,
 ReadSuppliers=function()return {base=resource==1 and {{plot=796,resource='RESOURCE_CATTLE',ready=true,working=false}}or {}}end}
'''


class WashingtonOpportunity(unittest.TestCase):
    def test_all_source_guards_precede_resource_removal(self):
        for changed in('hidden=true','unknown=true','anotherBase=true','owner=2','resource=2'):
            with self.subTest(changed=changed):
                vm=LuaRuntime();vm.execute(FIXTURE+changed)
                with self.assertRaises(Exception):vm.execute(PREPARE)
                self.assertEqual(vm.globals().writes,0)

    def test_restore_exact_source_once_without_publishing(self):
        vm=LuaRuntime();vm.execute(FIXTURE);vm.execute(PREPARE)
        self.assertTrue(vm.globals().initialized)
        self.assertEqual((vm.globals().resource,vm.globals().writes),(-1,1))
        vm.execute(RESTORE)
        self.assertEqual((vm.globals().resource,vm.globals().count,vm.globals().writes),(1,1,2))
        self.assertEqual(vm.globals().scope,1) # Only an ordinary later commit retires it.
        with self.assertRaises(Exception):vm.execute(RESTORE)
        self.assertEqual(vm.globals().writes,2)

    def test_missing_scope_or_changed_queue_refuses_restore(self):
        for changed in('scope=0','queued="UNIT_WARRIOR"','gold=46','population=5'):
            with self.subTest(changed=changed):
                vm=LuaRuntime();vm.execute(FIXTURE);vm.execute(PREPARE);vm.execute(changed)
                with self.assertRaises(Exception):vm.execute(RESTORE)
                self.assertEqual(vm.globals().writes,1)

    def test_fixture_is_after_includes_and_before_main_initialization(self):
        root=Path(__file__).resolve().parents[4]/'Civ Supply Chains/Lua_UI/AI'
        original=(root/'CSC_AI_BakersGameplay.lua').read_bytes();modified=stage(original)
        text=modified.decode('utf-8-sig')
        self.assertLess(text.index("include('CSC_AI_QuarterPlacement')"),text.index('CSC_WASH_OPPORTUNITY_STATE==nil'))
        self.assertLess(text.index('CSC_WASH_BASE_ABSENT'),text.index('local identityPrefix'))
        self.assertEqual(modified.count(b'    CSC_WASH_OPPORTUNITY_Snapshot()'),1)
        LuaRuntime().eval('function(s)assert(loadstring(s))end')(text)


if __name__=='__main__':unittest.main()
