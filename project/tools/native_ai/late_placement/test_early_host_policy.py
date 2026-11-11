"""Keep legacy-seat migration atomic and staged host telemetry passive."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
from early_host_policy import ROLE_PREFIX,stage


FIXTURE='''
print=function()end;writes=0;properties={};humans={[0]=true};major={};alive={};leaders={}
local expected={'LEADER_CLEOPATRA','LEADER_GANDHI','LEADER_TOMYRIS',
 'LEADER_T_ROOSEVELT','LEADER_VICTORIA','LEADER_HOJO'}
Players={};PlayerConfigurations={}
for pid=0,5 do
 local id=pid;leaders[id]=expected[id+1];major[id]=true;alive[id]=true
 Players[id]={IsHuman=function()return humans[id]==true end,
  IsMajor=function()return major[id]end,IsAlive=function()return alive[id]end}
 PlayerConfigurations[id]={GetLeaderTypeName=function()return leaders[id]end}
end
Game={GetCurrentGameTurn=function()return 22 end,
 GetProperty=function(_,key)if properties[key]~=nil then return properties[key]end end,
 SetProperty=function(_,key,value)writes=writes+1;properties[key]=value end}
cityName='LOC_CITY_NAME_BOSTON'
CityManager={GetCity=function(pid,cid)assert(pid==3 and cid==131073)
 return {GetName=function()return cityName end}end}
'''


class EarlyHostPolicy(unittest.TestCase):
    def test_every_seat_is_checked_before_any_migration(self):
        for change in ('properties.CSC_AI_OriginalHuman_5=1','leaders[5]="OTHER"',
                'humans[5]=true','major[5]=false','alive[5]=false',
                'PlayerConfigurations[5]=nil','Players[5]=nil','cityName="OTHER"'):
            with self.subTest(change=change):
                vm=LuaRuntime();vm.execute(FIXTURE+change)
                with self.assertRaises(Exception):vm.execute(ROLE_PREFIX)
                self.assertEqual(vm.globals().writes,0)

    def test_matching_existing_properties_are_preserved(self):
        for existing,expected in [('',6),('properties.CSC_AI_OriginalHuman_0=1;properties.CSC_AI_OriginalHuman_5=0',4)]:
            vm=LuaRuntime();vm.execute(FIXTURE+existing);vm.execute(ROLE_PREFIX)
            self.assertEqual(vm.globals().writes,expected)
            for pid in range(6):self.assertEqual(vm.globals().properties['CSC_AI_OriginalHuman_'+str(pid)],1 if pid==0 else 0)

    def test_facts_are_after_capacity_and_do_not_replace_policy_model(self):
        root=Path(__file__).resolve().parents[4]/'Civ Supply Chains/Lua_UI/AI'
        scanner=(root/'CSC_AI_AdjacencyScan.lua').read_bytes()
        publisher=(root/'CSC_AI_BakersGameplay.lua').read_bytes()
        modified_scanner,modified_publisher=stage(scanner,publisher)
        self.assertEqual(modified_scanner.count(b'candidate.diagnosticFutureDistrict'),1)
        self.assertEqual(modified_scanner.count(b'adjacency=score('),scanner.count(b'adjacency=score('))
        code=modified_publisher.decode('utf-8-sig')
        self.assertLess(code.index('for i = #entries, capacity + 1, -1'),code.index('    CSC_EARLY_DIAG_Retained(entries,turn,version+1)'))
        self.assertLess(code.index('    CSC_EARLY_DIAG_Retained(entries,turn,version+1)'),code.index('local accepted, message = bridge.Publish('))
        for source in (modified_scanner,modified_publisher):
            LuaRuntime().eval('function(code)return assert(loadstring(code))end')(source.decode('utf-8-sig'))


if __name__=='__main__':unittest.main()
