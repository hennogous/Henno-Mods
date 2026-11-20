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

    def test_material_work_and_prerequisite_bids_share_the_same_commit(self):
        l = self.make('''
CE_AIMaterialDevelopmentStatus=function()return
    '{"abi":1,"techReady":1,"civicReady":0,"builderReady":1,"researchLimitQ8":16384,"builderLimitQ8":32768,"workerReady":1,"workerFinishOnly":1,"workerLoanReady":1}'
end
CE_AIBuilderProtectionBid=function(player,city,plot,improvement,deltaQ8)
    assert(player==1 and city==42 and plot==123 and improvement==4 and deltaQ8==17995)
    calls[#calls+1]='Job';return 1
end
CE_AIMaterialResearchBid=function(player,kind,index,deltaQ8)
    assert(player==1 and kind==0 and index==17 and deltaQ8==2048)
    calls[#calls+1]='Research';return 1
end
CE_AIMaterialBuilderRequestBid=function(player,city,plot,improvement,unit,deltaQ8)
    assert(player==1 and city==42 and plot==123 and improvement==4 and unit==5 and deltaQ8==8192)
    calls[#calls+1]='Request';return 1
end
CE_AIMaterialWorkerFinishOffer=function(player,city,plot,improvement,unit,unitType,x,y)
    assert(player==1 and city==42 and plot==123 and improvement==4 and unit==39 and unitType==5 and x==49 and y==1)
    calls[#calls+1]='Worker';return 1
end
CE_AIMaterialWorkerLoanOffer=function(player,city,plot,improvement,unit,unitType,x,y,artifact)
    assert(player==1 and city==42 and plot==123 and improvement==4 and unit==40 and unitType==5
        and x==47 and y==1 and artifact==47)
    calls[#calls+1]='Loan';return 1
end
function publishDevelopment()
    local b=CSC_AI_DistrictBridge
    local status=b.MaterialDevelopmentStatus()
    assert(select(4,b.MaterialDevelopmentLimits(status))==0)
    assert(select(4,b.MaterialDevelopmentLimits('{"abi":1,"workerReady":1}',true))==0)
    assert(select(5,b.MaterialDevelopmentLimits('{"abi":1,"workerReady":1}',true))==false)
    local tech,civic,builder,workerLimit,loanReady=b.MaterialDevelopmentLimits(status,true)
    assert(tech==16384 and civic==0 and builder==32768 and workerLimit==4 and loanReady)
    assert(b.BuilderBidLimit('{"maxBidQ8":16384}')==16384)
    local jobLimit=b.BuilderBidLimit('{"maxBidQ8":32768}')
    assert(jobLimit==32768)
    local job={player=1,city=42,plot=123,improvements={4},deltaQ8=17995}
    local topic={player=1,kind=0,index=17,deltaQ8=2048}
    local request={player=1,city=42,plot=123,improvement=4,unit=5,deltaQ8=8192}
    local worker={player=1,city=42,plot=123,improvement=4,unit=39,unitType=5,x=49,y=1}
    local loan={player=1,city=42,plot=123,improvement=4,unit=40,unitType=5,x=47,y=1,artifact=47}
    return b.Publish(1,74,46,80,{1},packet,{job},false,false,jobLimit,
        {},0,nil,0,{},nil,0,{},0,{}, {},{topic},{request},{worker},{loan})
end
''')
        self.assertTrue(l.eval('publishDevelopment()'))
        self.assertEqual(l.eval("table.concat(calls,',')"), 'Begin,Allow,Entry,Job,Research,Request,Worker,Loan,Commit')

if __name__=='__main__':unittest.main()
