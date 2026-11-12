"""Main CSC ownership metadata: optional fallback, live fanout and receipt timing.

Use the existing isolated Lua51 dependency. This exercises the actual publisher
and bridge; it does not establish native acknowledgement or construction.
"""
import importlib.util
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'Civ Supply Chains/Lua_UI/AI'
spec=importlib.util.spec_from_file_location('ownership_base_fixture',
    ROOT/'project/tools/ai_workshop_bridge/ce_frontend/test_bakers_gameplay.py')
fixture=importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


def runtime(capability=True,capacity=4096):
    lua=LuaRuntime();lua.execute(fixture.FIXTURE)
    messages=[];lua.globals().print=lambda *args:messages.append(' '.join(map(str,args)))
    def include(name):
        if name!='CSC_AdjacencyCore':lua.execute((SOURCE/(name+'.lua')).read_text(encoding='utf-8-sig'))
    lua.globals().include=include
    include('CSC_AI_BakersGameplay')
    lua.execute('''
ExposedMembers.CSC_Adjacency={IsSinglePlayer=function()return true end}
CSC_AI_QuarterPlacement.MaterialDeductions=function()return {},{},{},{},{},{}end
CSC_AI_QuarterSiteForecasts=function()return {},{legal=0}end
CSC_AI_QuarterPlacement.StageTwoProfiles=function()return {{district={Index=2}},{district={Index=3}}}end
local first=city
first.GetDistricts=function()return {HasDistrict=function(_,d)return d==3 end}end
local second={GetID=function()return 99 end,GetDistricts=function()
 return {HasDistrict=function(_,d)return built and d==3 end}end}
Players[3].GetCities=function()return {Members=function()
 local rows={first,second};local i=0
 return function()i=i+1;if rows[i]then return i,rows[i]end end end}end
ownScopes={};ownCalls=0;ownReady=true
local begin=CE_AIDistrictScoresBegin
CE_AIDistrictScoresBegin=function(v)ownScopes={};return begin(v)end
''')
    if capability:
        lua.execute('''
CE_AIDistrictPurchaseCompletionStatus=function()
 return '{"ready":'..(ownReady and '1' or '0')..',"faults":0,"capacity":CAPACITY,"acknowledged":'..(version==1 and '1' or '0')..'}'
end
CE_AIDistrictPurchaseCompletionStage=function(p,c,d)
 assert(p==3);ownCalls=ownCalls+1;ownScopes[#ownScopes+1]={p,c,d};return rejectScope and 0 or 1
end
CE_AIDistrictPurchaseCompletionReceipt=function(v,p,c,d)
 assert(v==version and v==1)
 return '{"staged":1,"acknowledged":'..((c==99 and d==3)and '1' or '0')..'}'
end
'''.replace('CAPACITY',str(capacity)))
    return lua,messages


class OwnershipPublication(unittest.TestCase):
    def test_missing_optional_api_keeps_ordinary_publication(self):
        lua,messages=runtime(False);lua.execute('boundary()')
        self.assertTrue(lua.eval('packet~=nil and version==1'))
        self.assertEqual(lua.eval('ownCalls'),0)
        self.assertFalse(any('DISTRICTS_FAILED' in s for s in messages))
        lua.execute('''
local ok=CSC_AI_DistrictBridge.Publish(2,40,30,4,{3},{},nil,false,false,0,nil,0,nil,0,nil,{},0)
assert(ok and packet~=nil) -- Empty optional table cannot disable the old CE.
''')

    def test_live_cities_profiles_and_prior_receipt_survive_foundation(self):
        lua,messages=runtime();lua.execute('boundary()')
        rows=[tuple(row.values())for row in lua.globals().ownScopes.values()]
        self.assertEqual(rows,[(3,42,2),(3,99,2),(3,99,3)])
        lua.execute('built=true;turn=2;boundary()')
        self.assertEqual([tuple(r.values())for r in lua.globals().ownScopes.values()],[(3,42,2),(3,99,2)])
        self.assertTrue(any('OWNERSHIP_RECEIPT turn=2 version=1 player=3 city=99 district=3' in s for s in messages))

    def test_unready_and_over_capacity_preserve_score_guidance(self):
        lua,_=runtime();lua.execute('ownReady=false;boundary()')
        self.assertTrue(lua.eval('packet~=nil and version==1'));self.assertEqual(lua.eval('ownCalls'),0)
        lua,messages=runtime(capacity=2);lua.execute('boundary()')
        self.assertTrue(lua.eval('packet~=nil and version==1'));self.assertEqual(lua.eval('ownCalls'),0)
        self.assertTrue(any('OWNERSHIP_COMPLETION turn=1 scopes=0 omitted=3' in s for s in messages))

    def test_native_rejection_and_duplicate_scopes_fail_closed(self):
        lua,messages=runtime();lua.execute('rejectScope=true;boundary()')
        self.assertTrue(lua.eval('packet==nil'))
        self.assertTrue(any('Native ownership scope rejected' in s for s in messages))
        lua,_=runtime();lua.execute('''
local ok=CSC_AI_DistrictBridge.Publish(1,40,30,4,{3},{},nil,false,false,0,nil,0,nil,0,nil,
 {{player=3,city=42,district=3},{player=3,city=42,district=3}},4096)
assert(not ok and ownCalls==0)
''')


if __name__=='__main__':unittest.main()
