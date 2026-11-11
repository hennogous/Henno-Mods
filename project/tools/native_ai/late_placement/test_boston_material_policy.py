"""Guard the one-pair ablation and saved-role boundary before native replay."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
from boston_material_policy import PREFIX,FILTER,stage,PREPARE_SPECIALTY


class BostonPolicy(unittest.TestCase):
    def test_only_target_positive_entry_is_removed(self):
        for control in (False,True):
            vm=LuaRuntime()
            vm.execute('''print=function()end;turn=22;version=1
builderSites={};nominations={};repairs={};exclusions={}
entries={{player=3,city=131073,district=36,plot=721,delta=6144},
 {player=3,city=131073,district=36,plot=720,delta=-65536},
 {player=3,city=65536,district=36,plot=721,delta=6144},
 {player=3,city=131073,district=37,plot=721,delta=6144}}
''')
            vm.globals().CSC_MATERIAL_DIAG_CONTROL=control
            vm.execute(FILTER)
            rows=list(vm.globals().entries.values())
            self.assertEqual(len(rows),3 if control else 4)
            self.assertEqual([(r.city,r.district,r.plot,r.delta)for r in rows],
                ([(131073,36,721,6144)] if not control else [])+
                [(131073,36,720,-65536),(65536,36,721,6144),(131073,37,721,6144)])
            self.assertEqual(vm.globals().CSC_MATERIAL_DIAG_INITIAL.matches,1)
            self.assertEqual(vm.globals().CSC_MATERIAL_DIAG_INITIAL.removed,int(control))

    def test_duplicate_target_is_rejected_in_both_arms(self):
        for control in (False,True):
            vm=LuaRuntime()
            vm.execute('''print=function()end;turn=22;version=1
builderSites={};nominations={};repairs={};exclusions={}
local row={player=3,city=131073,district=36,plot=721,delta=6144}
entries={row,row}''')
            vm.globals().CSC_MATERIAL_DIAG_CONTROL=control
            with self.assertRaisesRegex(Exception,'Duplicate material-policy target'):
                vm.execute(FILTER)

    def test_role_conflicts_fail_before_writing(self):
        fixture='''print=function()end;writes=0;previous=nil;turn=22;human=false;leader='LEADER_T_ROOSEVELT'
Players={[0]={IsHuman=function()return true end},[3]={IsHuman=function()return human end}}
CityManager={GetCity=function()return {GetName=function()return 'LOC_CITY_NAME_BOSTON' end}end}
PlayerConfigurations={[3]={GetLeaderTypeName=function()return leader end}}
Game={GetCurrentGameTurn=function()return turn end,
 GetProperty=function()if previous~=nil then return previous end end,
 SetProperty=function(_,key,value)writes=writes+1;previous=value end}
GameEvents={OnGameTurnStarted={Add=function()end}}
'''
        for change,valid in [('',True),('previous=0',True),('previous=1',False),
                ('turn=23',False),('human=true',False),('leader="OTHER"',False)]:
            with self.subTest(change=change):
                vm=LuaRuntime();vm.execute(fixture+change)
                prefix=PREFIX.replace('__CONTROL__','false').replace('__THROUGH__','33')
                if valid:
                    vm.execute(prefix);self.assertEqual(vm.globals().writes,0 if change else 1)
                else:
                    with self.assertRaises(Exception):vm.execute(prefix)
                    self.assertEqual(vm.globals().writes,0)

    def test_staging_is_after_capacity_and_compiles(self):
        path=Path(__file__).resolve().parents[4]/'Civ Supply Chains/Lua_UI/AI/CSC_AI_BakersGameplay.lua'
        source=path.read_bytes()
        for arm in ('control','treatment'):
            for delta in (6144,12288):
                modified=stage(source,arm,33,delta).decode('utf-8-sig')
                self.assertLess(modified.index('for i = #entries, capacity + 1, -1'),modified.index(FILTER))
                self.assertLess(modified.index(FILTER),modified.index('local accepted, message = bridge.Publish('))
                self.assertNotIn('__DELTA__',modified)
                LuaRuntime().eval('function(code)return assert(loadstring(code))end')(modified)
        with self.assertRaises(AssertionError):stage(source,'treatment',33,10730)

    def test_specialty_preparation_preserves_host_and_rejects_changed_source(self):
        fixture='''
print=function()end;writes=0;revealed=true;suitable=true
city={GetID=function()return 131073 end,GetName=function()return 'LOC_CITY_NAME_BOSTON' end}
CityManager={GetCity=function()return city end}
Players={[0]={IsHuman=function()return true end},[3]={IsHuman=function()return false end,
 GetTreasury=function()return {GetGoldBalance=function()return 50 end}end}}
Game={GetCurrentGameTurn=function()return 22 end}
GameInfo={Resources={RESOURCE_SUGAR={Index=2},RESOURCE_CATTLE={Index=1},[1]={ResourceType='RESOURCE_CATTLE'}},
 Terrains={[0]={TerrainType='TERRAIN_GRASS'}},Features={[0]={FeatureType='FEATURE_MARSH'}}}
plots={}
for _,index in ipairs({721,796,720,722})do
 local p={index=index,owner=index==722 and -1 or 3,resource=index==796 and 1 or -1,feature=0}
 function p:GetOwner()return self.owner end
 function p:GetResourceType()return self.resource end
 function p:GetDistrictType()return -1 end
 function p:GetImprovementType()return -1 end
 function p:GetTerrainType()return 0 end
 function p:GetFeatureType()return self.feature end
 function p:GetX()return self.index end
 function p:GetY()return 0 end
 plots[index]=p
end
Map={GetPlotByIndex=function(index)return plots[index]end}
Cities={GetPlotPurchaseCity=function()return city end}
PlayersVisibility={[3]={IsRevealed=function()return revealed end}}
ResourceBuilder={CanHaveResource=function()return suitable end,
 SetResourceType=function(p,index,count)assert(count==1);writes=writes+1;p.resource=index end}
WorldBuilder={CityManager=function()return {SetPlotOwner=function(_,x,y,pid,cid)
 assert(x==722 and y==0 and pid==3 and cid==131073);writes=writes+1;plots[x].owner=pid end}end}
'''
        for change in ('','plots[722].owner=3','plots[722].resource=1',
                'revealed=false','suitable=false','plots[722].feature=-1','plots[720].resource=1',
                'ResourceBuilder.SetResourceType=nil'):
            with self.subTest(change=change):
                vm=LuaRuntime();vm.execute(fixture+change)
                if not change:
                    vm.execute(PREPARE_SPECIALTY)
                    self.assertEqual(vm.globals().writes,2)
                    self.assertEqual(vm.globals().plots[720].resource,-1)
                    self.assertEqual(vm.globals().plots[796].resource,1)
                    self.assertEqual(vm.globals().plots[722].resource,2)
                else:
                    with self.assertRaises(Exception):vm.execute(PREPARE_SPECIALTY)
                    self.assertEqual(vm.globals().writes,0)


if __name__=='__main__':unittest.main()
