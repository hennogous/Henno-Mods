"""Exercise the actual CE-only consumer against a small native-API fixture."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
SOURCE=(Path(__file__).resolve().parents[4]/'Civ Supply Chains/Lua_UI/AI/CSC_AI_DistrictBridge.lua').read_text(encoding='utf-8')
FIXTURE='''calls={};disabled=false
for _,name in ipairs({'Begin','Allow','Entry','Commit','Disable','Status'}) do
 local n=name
 _G['CE_AIDistrictScores'..name]=function(...)
  calls[#calls+1]=n
  if n=='Disable' then disabled=true end
  if n==fail then return 0 end
  return 1
 end
end
packet={{player=1,city=65536,district=36,plot=2,delta=256}}
'''
class FrontendTests(unittest.TestCase):
    def make(self,extra=''):
        lua=LuaRuntime(unpack_returned_tuples=True);lua.execute(FIXTURE+extra);lua.execute(SOURCE);return lua
    def test_stock_CE_without_new_API_is_unavailable(self):
        l=LuaRuntime(unpack_returned_tuples=True);l.execute(SOURCE)
        self.assertFalse(l.eval('CSC_AI_DistrictBridge.Available()'))
        self.assertFalse(l.eval('CSC_AI_DistrictBridge.Publish(1,74,46,80,{}, {})')[0])
    def test_valid_packet_uses_only_batch_API(self):
        l=self.make();self.assertTrue(l.eval('CSC_AI_DistrictBridge.Publish(1,74,46,80,{1},packet)'))
        self.assertEqual(l.eval('table.concat(calls,",")'),'Begin,Allow,Entry,Commit')
    def test_duplicate_packet_disables_before_begin(self):
        l=self.make('packet[2]=packet[1];')
        self.assertFalse(l.eval('CSC_AI_DistrictBridge.Publish(1,74,46,80,{1},packet)')[0])
        self.assertEqual(l.eval('table.concat(calls,",")'),'Disable')
    def test_unapproved_identity_is_rejected(self):
        l=self.make('packet[1].player=0;')
        self.assertFalse(l.eval('CSC_AI_DistrictBridge.Publish(1,74,46,80,{1},packet)')[0])
        self.assertEqual(l.eval('table.concat(calls,",")'),'Disable')
    def test_native_entry_failure_disables_without_commit(self):
        l=self.make('fail="Entry";')
        self.assertFalse(l.eval('CSC_AI_DistrictBridge.Publish(1,74,46,80,{1},packet)')[0])
        self.assertEqual(l.eval('table.concat(calls,",")'),'Begin,Allow,Entry,Disable')
    def test_gameplay_environment_without_G_alias(self):
        l=self.make('_G=nil;')
        self.assertTrue(l.eval('CSC_AI_DistrictBridge.Available()'))
        self.assertTrue(l.eval('CSC_AI_DistrictBridge.Publish(1,74,46,80,{1},packet)'))
    def test_havok_native_integer_type_tag(self):
        l=self.make("local baseType=type;function type(x) if baseType(x)=='number'and x==math.floor(x)then return 'integer' end;return baseType(x)end")
        self.assertTrue(l.eval('CSC_AI_DistrictBridge.Publish(1,74,46,80,{1},packet)'))
if __name__=='__main__':unittest.main()
