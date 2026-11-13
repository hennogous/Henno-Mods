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
    def test_complete_value_uses_exclusive_native_final_transport(self):
        l=self.make('''
CE_AIDistrictScoresFinalEntry=function(...)calls[#calls+1]='FinalEntry';return 1 end
packet[1].delta=0;packet[1].finalQ8=-16384
''')
        self.assertTrue(l.eval('CSC_AI_DistrictBridge.Publish(1,74,46,80,{1},packet)'))
        self.assertIn('FinalEntry',l.eval("table.concat(calls,',')"))
        self.assertNotIn(',Entry,',','+l.eval("table.concat(calls,',')")+',')
    def test_complete_value_without_native_support_is_rejected_before_begin(self):
        l=self.make('packet[1].delta=0;packet[1].finalQ8=0')
        self.assertFalse(l.eval('CSC_AI_DistrictBridge.Publish(1,74,46,80,{1},packet)')[0])
        self.assertEqual(l.eval("table.concat(calls,',')"),'Disable')
    def managed(self,extra=''):
        return self.make('''
CE_AIDistrictScoresManagedType=function(...)calls[#calls+1]='ManagedType';return 1 end
CE_AIDistrictScoresFinalEntry=function(...)calls[#calls+1]='FinalEntry';return 1 end
packet[1].delta=0;packet[1].finalQ8=100
managed={{player=1,district=36,fallbackQ8=-262144}}
function publishManaged()
 return CSC_AI_DistrictBridge.Publish(1,74,46,80,{1},packet,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,managed)
end
'''+extra)
    def test_managed_defaults_stage_before_complete_offers(self):
        l=self.managed();self.assertTrue(l.eval('publishManaged()'))
        self.assertEqual(l.eval("table.concat(calls,',')"),'Begin,Allow,ManagedType,FinalEntry,Commit')
    def test_managed_default_cannot_be_positive(self):
        l=self.managed('managed[1].fallbackQ8=1')
        self.assertFalse(l.eval('publishManaged()')[0])
        self.assertEqual(l.eval("table.concat(calls,',')"),'Disable')
    def test_managed_default_rejects_mixed_additive_and_duplicate_scope(self):
        for extra in ('packet[1].finalQ8=nil;packet[1].delta=256','managed[2]=managed[1]'):
            l=self.managed(extra);self.assertFalse(l.eval('publishManaged()')[0])
            self.assertEqual(l.eval("table.concat(calls,',')"),'Disable')
    def test_managed_scopes_allow_new_cities_without_site_entries(self):
        l=self.managed('packet={}')
        self.assertTrue(l.eval('publishManaged()'))
        self.assertEqual(l.eval("table.concat(calls,',')"),'Begin,Allow,ManagedType,Commit')

if __name__=='__main__':unittest.main()
