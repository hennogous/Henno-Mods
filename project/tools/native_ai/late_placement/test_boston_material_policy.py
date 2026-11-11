"""Guard the one-pair ablation and saved-role boundary before native replay."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
from boston_material_policy import PREFIX,FILTER,stage


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
            modified=stage(source,arm,33).decode('utf-8-sig')
            self.assertLess(modified.index('for i = #entries, capacity + 1, -1'),modified.index(FILTER))
            self.assertLess(modified.index(FILTER),modified.index('local accepted, message = bridge.Publish('))
            LuaRuntime().eval('function(code)return assert(loadstring(code))end')(modified)


if __name__=='__main__':unittest.main()
