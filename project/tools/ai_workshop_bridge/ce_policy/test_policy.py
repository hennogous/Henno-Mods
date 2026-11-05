"""Actual Lua-vs-Python policy comparison and packaged lifecycle fixtures.

Run with the existing Lupa directory in PYTHONPATH. No test launches Civ or
imports a Frida worker. Real cases are bounded copies from source-hashed scans.
"""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import random
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from lupa.lua51 import LuaRuntime

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
POLICY_SOURCE=(HERE/'policy.lua').read_text(encoding='utf-8')
GAMEPLAY_SOURCE=(HERE/'gameplay.lua').read_text(encoding='utf-8')
FRONTEND=(HERE.parent/'ce_frontend/CSC_AI_DistrictBridge.lua').read_text(encoding='utf-8')
spec=importlib.util.spec_from_file_location('reference_policy',ROOT/'project/tools/ai_site_planner/adjacency_policy/policy.py')
REFERENCE=importlib.util.module_from_spec(spec);spec.loader.exec_module(REFERENCE)
spec=importlib.util.spec_from_file_location('ce_policy_builder',HERE/'build.py')
BUILDER=importlib.util.module_from_spec(spec);spec.loader.exec_module(BUILDER)

def fixture():
    return dict(turn=20,originalAI=[1,2],currentHumans=[0],candidates=[dict(player=1,city=7,district=8,plot=30,
        quarter='BAKERS',production=2,gold=2,total=4,materialOnSite=False,legal=True)])

def to_lua(lua,value):
    if isinstance(value,dict):return lua.table_from({k:to_lua(lua,v)for k,v in value.items()})
    if isinstance(value,list):return lua.table_from([to_lua(lua,v)for v in value])
    return value

def to_python(value):
    if hasattr(value,'items'):
        items=dict(value.items())
        if set(items)==set(range(1,len(items)+1)):return [to_python(items[i])for i in range(1,len(items)+1)]
        return {k:to_python(v)for k,v in items.items()}
    return value

def logical_receipts(lines):
    """Test decoder for the disk framing contract; not a native/game client."""
    groups={};result=[]
    for line in lines:
        match=re.search(r'CSC_CE_POLICY_([A-Z_]+)=(.*)',line)
        if not match or match[1]=='STATE':continue
        kind,value=match[1],json.loads(match[2])
        if kind!='CHUNK':result.append((kind,value));continue
        frame=value;key=(frame['epoch'],frame['seq'])
        if frame['schema']!=1 or frame['encoding']!='hex':raise ValueError('Invalid chunk schema')
        metadata={k:frame[k]for k in ('schema','epoch','seq','kind','parts','bytes','sum32','encoding')}
        group=groups.setdefault(key,dict(metadata=metadata,parts=[]))
        if group['metadata']!=metadata or frame['part']!=len(group['parts'])+1:raise ValueError('Out-of-order chunk')
        group['parts'].append(bytes.fromhex(frame['data']))
        if frame['part']==frame['parts']:
            payload=b''.join(group['parts'])
            if len(payload)!=frame['bytes'] or sum(payload)%4294967296!=frame['sum32']:raise ValueError('Incomplete/changed payload')
            result.append((frame['kind'],json.loads(payload.decode('utf-8'))));group['complete']=True
    if any(not g.get('complete')for g in groups.values()):raise ValueError('Missing chunk')
    return result

HARNESS=r'''
receipts={};function print(text)receipts[#receipts+1]=text end
function include(name)end
turn=1;mode=nil;properties={};human0=true
Game={GetCurrentGameTurn=function()return turn end,
 GetProperty=function(self,key)return properties[key]end,
 SetProperty=function(self,key,value)properties[key]=value end}
GameConfiguration={GetValue=function(key)return mode end}
Players={}
for pid=0,1 do local id=pid;Players[id]={IsAlive=function()return true end,IsMajor=function()return true end,
 IsHuman=function()return id==0 and human0 end}end
CSC_Adjacency={Initialize=function() initialized=true end}
scanCount=0
function CSC_AI_AdjacencyScan(originalAI)
 scanCount=scanCount+1;snapshot.turn=turn;snapshot.originalAI=originalAI
 snapshot.currentHumans=human0 and {0}or{};return snapshot
end
function event()return {Add=function(fn)listeners[#listeners+1]=fn end}end
listeners={};GameEvents={OnGameTurnStarted=event()};Events={PlayerTurnActivated=event(),LoadScreenClose=event()}
native={version=0,enabled=0,ready=1,faults=0,entries=0,generation=0,trace_count=0};nativeRows={};calls={}
function CE_AIDistrictScoresStatus()
 return '{"version":'..native.version..',"enabled":'..native.enabled..',"ready":'..native.ready..',"faults":'..native.faults..',"entries":'..native.entries..',"generation":'..native.generation..',"trace_count":'..native.trace_count..'}'
end
function CE_AIDistrictScoresBegin(v,w,h,d)
 calls[#calls+1]='Begin';native.enabled=0;native.version=v;nativeRows={};native.entries=0;native.trace_count=0;native.generation=native.generation+1;return 1
end
function CE_AIDistrictScoresAllow(pid)calls[#calls+1]='Allow';return 1 end
function CE_AIDistrictScoresEntry(p,c,d,plot,delta)
 calls[#calls+1]='Entry';if failEntry then return 0 end
 nativeRows[#nativeRows+1]={player=p,city=c,district=d,plot=plot,delta=delta};native.entries=#nativeRows;return 1
end
function CE_AIDistrictScoresCommit()calls[#calls+1]='Commit';native.enabled=1;return 1 end
function CE_AIDistrictScoresDisable()calls[#calls+1]='Disable';native.enabled=0;native.generation=native.generation+1;return 1 end
function CE_AIDistrictScoresTraceRead(offset,limit,generation)
 calls[#calls+1]='TraceRead';assert(native.enabled==0,'trace not frozen')
 return '{"generation":'..native.generation..',"next":'..(offset+limit)..',"stale":false,"records":[]}'
end
'''

class PolicyParityTests(unittest.TestCase):
    def setUp(self):
        self.lua=LuaRuntime(unpack_returned_tuples=True);self.lua.execute(POLICY_SOURCE)
    def compare(self,snapshot):
        expected=REFERENCE.shortlist(copy.deepcopy(snapshot))
        actual=to_python(self.lua.globals().CSC_AI_AdjacencyPolicy.Shortlist(to_lua(self.lua,snapshot)))
        self.assertEqual(actual,expected)
    def test_actual_captured_source_subsets(self):
        cases=json.loads((HERE/'fixtures/captured.json').read_text())['cases']
        for case in cases:
            with self.subTest(turn=case['snapshot']['turn']):self.compare(case['snapshot'])
    def test_gradient_fractional_rounding_and_negative_cap(self):
        for total in [5,4,3.99999,3.5,3,2,1,0,-1]:
            s=fixture();s['candidates'][0].update(production=total-2,total=total);self.compare(s)
    def test_competing_quarters_city_ties_and_resource_preservation(self):
        s=fixture()
        for city,quarter,plot,total,material in [(7,'TAILORS',3,5,False),(7,'BAKERS',4,5,False),
            (7,'BAKERS',2,5,False),(8,'TAILORS',5,6,False),(8,'BAKERS',6,7,True),
            (8,'TAILORS',7,1,True)]:
            r=copy.deepcopy(s['candidates'][0]);r.update(city=city,quarter=quarter,plot=plot,total=total,
                production=total-2,materialOnSite=material);s['candidates'].append(r)
        self.compare(s)
    def test_seeded_multi_city_pair_comparisons(self):
        rng=random.Random(26131103)
        for _ in range(50):
            s=fixture();s['candidates']=[]
            for i in range(40):
                p=rng.choice([1,2]);c=rng.randrange(3);d=rng.choice([8,9]);total=rng.randrange(-2,15)/2
                s['candidates'].append(dict(player=p,city=c,district=d,plot=i,quarter='BAKERS'if d==8 else'TAILORS',
                    production=total-2,gold=2,total=total,materialOnSite=rng.choice([True,False]),legal=True))
            self.compare(s)
    def test_scope_duplicate_totals_and_endpoint_rejections(self):
        bad=[]
        s=fixture();s['currentHumans']=[1];bad.append(s)
        s=fixture();s['candidates'][0]['player']=3;bad.append(s)
        s=fixture();s['candidates']*=2;bad.append(s)
        s=fixture();s['candidates'][0]['total']=float('nan');bad.append(s)
        s=fixture();s['candidates'][0]['gold']=3;bad.append(s)
        s=fixture();s['turn']=101;bad.append(s)
        for s in bad:
            with self.assertRaises(Exception):REFERENCE.shortlist(s)
            with self.assertRaises(Exception):self.lua.globals().CSC_AI_AdjacencyPolicy.Shortlist(to_lua(self.lua,s))
    def test_capacity_boundary(self):
        s=fixture();base=s['candidates'][0]
        s['candidates']=[dict(base,plot=i,total=1,production=-1)for i in range(4096)]
        self.compare(s)
        s['candidates'].append(dict(base,plot=4096,total=1,production=-1))
        with self.assertRaises(Exception):REFERENCE.shortlist(s)
        with self.assertRaises(Exception):self.lua.globals().CSC_AI_AdjacencyPolicy.Shortlist(to_lua(self.lua,s))

class PackagedLifecycleTests(unittest.TestCase):
    def make(self,extra=''):
        lua=LuaRuntime(unpack_returned_tuples=True);lua.execute(HARNESS)
        s=fixture();s.update(turn=1,width=74,height=46,districtCount=38,speed='GAMESPEED_ONLINE',cities=[],
            sitesEvaluated=1,geometryBuilt=1,elapsedSeconds=0)
        lua.globals().snapshot=to_lua(lua,s)
        lua.execute(FRONTEND);lua.execute(POLICY_SOURCE);lua.execute(extra);lua.execute(GAMEPLAY_SOURCE)
        return lua
    def test_initial_identity_excludes_original_human_before_autoplay(self):
        l=self.make();self.assertEqual(to_python(l.eval('CSC_CE_PolicyStatus().originalAI')),[1])
        self.assertFalse(l.eval('CSC_CE_PolicyStatus().failed'));self.assertEqual(l.eval('native.enabled'),1)
        l.execute('human0=false;turn=2;CSC_AI_CEPolicy.Refresh("test-boundary")')
        self.assertEqual(to_python(l.eval('CSC_CE_PolicyStatus().originalAI')),[1])
        self.assertEqual(l.eval('scanCount'),2)
    def test_status_precedes_publication_and_full_report_is_valid_json(self):
        l=self.make();lines=to_python(l.globals().receipts)
        first=next(json.loads(s.split('=',1)[1])for s in lines if s.startswith('CSC_CE_POLICY_NATIVE='))
        self.assertEqual(first['status']['enabled'],0);self.assertEqual(first['status']['version'],0)
        l.execute('CSC_CE_PolicyReport()')
        report=json.loads(to_python(l.globals().receipts)[-1].split('=',1)[1])
        self.assertEqual(report['plan']['entries'][0]['delta'],1048576)
        self.assertEqual(json.loads(report['native'])['enabled'],1)
    def test_same_turn_events_do_not_replace_native_window(self):
        l=self.make();l.execute('CSC_AI_CEPolicy.Refresh("duplicate event")')
        self.assertEqual(l.eval('scanCount'),1);self.assertEqual(l.eval('native.version'),1)
    def test_disable_is_persistent_until_context_reload(self):
        l=self.make();self.assertTrue(l.eval('CSC_CE_PolicyDisable()'));l.execute('turn=2;CSC_AI_CEPolicy.Refresh("later")')
        self.assertEqual(l.eval('native.enabled'),0);self.assertEqual(l.eval('scanCount'),1)
        self.assertTrue(l.eval('CSC_CE_PolicyStatus().disabled'));self.assertFalse(l.eval('CSC_CE_PolicyStatus().failed'))
    def test_configured_off_context_preserves_native_reset(self):
        l=self.make('mode="off"')
        self.assertEqual(l.eval('native.enabled'),0);self.assertEqual(l.eval('native.version'),0)
        self.assertEqual(l.eval('scanCount'),0);self.assertFalse(l.eval('CSC_CE_PolicyStatus().failed'))
    def test_unmarked_old_save_refuses_scope_inference(self):
        l=self.make('turn=20;human0=false')
        self.assertTrue(l.eval('CSC_CE_PolicyStatus().failed'));self.assertEqual(l.eval('native.enabled'),0)
    def test_saved_identity_load_rebuilds_own_version_after_native_reset(self):
        l=self.make('turn=20;human0=false;properties.CSC_CE_POLICY_ORIGINAL_HUMAN_0=1;properties.CSC_CE_POLICY_ORIGINAL_HUMAN_1=0')
        self.assertFalse(l.eval('CSC_CE_PolicyStatus().failed'));self.assertEqual(l.eval('native.version'),1)
        self.assertEqual(to_python(l.eval('CSC_CE_PolicyStatus().originalAI')),[1])
    def test_failed_native_entry_disables_and_cannot_retry_implicitly(self):
        l=self.make('failEntry=true')
        self.assertTrue(l.eval('CSC_CE_PolicyStatus().failed'));self.assertEqual(l.eval('native.enabled'),0)
        l.execute('failEntry=false;turn=2;CSC_AI_CEPolicy.Refresh("retry event")')
        self.assertEqual(l.eval('scanCount'),1);self.assertEqual(l.eval('native.enabled'),0)
    def test_stock_CE_missing_capability_fails_closed(self):
        l=self.make('CE_AIDistrictScoresBegin=nil')
        self.assertTrue(l.eval('CSC_CE_PolicyStatus().failed'));self.assertEqual(l.eval('native.enabled'),0)
    def test_cleanup_disable_preserves_original_failure(self):
        l=self.make('failEntry=true')
        reason=l.eval('CSC_CE_PolicyStatus().reason')
        l.execute('CSC_CE_PolicyDisable()')
        self.assertTrue(l.eval('CSC_CE_PolicyStatus().failed'))
        self.assertEqual(l.eval('CSC_CE_PolicyStatus().reason'),reason)
    def test_endpoint_disables_before_new_scans(self):
        l=self.make();l.execute('turn=100;CSC_AI_CEPolicy.Refresh("endpoint")')
        self.assertEqual(l.eval('native.enabled'),0);self.assertEqual(l.eval('scanCount'),2)
        self.assertEqual(l.eval('CSC_CE_PolicyStatus().snapshot.turn'),100)
        self.assertEqual(l.eval('native.version'),1)
        self.assertEqual(l.eval('CSC_CE_PolicyStatus().reason'),'authorized endpoint')
    def test_gameplay_environment_without_G_alias(self):
        l=self.make('_G=nil')
        self.assertFalse(l.eval('CSC_CE_PolicyStatus().failed'));self.assertEqual(l.eval('native.enabled'),1)
    def test_trace_pages_are_frozen_and_preserved_before_next_begin(self):
        l=self.make();l.execute('native.trace_count=130;turn=2;CSC_AI_CEPolicy.Refresh("trace-test")')
        lines=to_python(l.globals().receipts)
        pages=[json.loads(s.split('=',1)[1])for s in lines if s.startswith('CSC_CE_POLICY_TRACE=')]
        self.assertEqual([p['page']['next']for p in pages],[64,128,130])
        self.assertEqual(l.eval('native.trace_count'),0)
        self.assertFalse(l.eval('CSC_CE_PolicyStatus().failed'))
    def test_intentionally_empty_object_remains_json_object(self):
        l=self.make('snapshot.emptyObject=setmetatable({},{__json_object=true})')
        l.execute('CSC_CE_PolicyReport()')
        report=json.loads(to_python(l.globals().receipts)[-1].split('=',1)[1])
        self.assertEqual(report['snapshot']['emptyObject'],{})
    def test_large_scan_plan_native_and_trace_survive_disk_line_limit(self):
        l=self.make('snapshot.unicode=string.rep("é水\\n",1000)')
        # Native long-string transport is separately tested in the CE module;
        # this fixture supplies an already complete >512-byte native JSON.
        l.execute('''
local oldStatus=CE_AIDistrictScoresStatus
function CE_AIDistrictScoresStatus()
 local raw=oldStatus();return raw:sub(1,-2)..',"longField":"'..string.rep('x',2500)..'"}'
end
native.trace_count=1
function CE_AIDistrictScoresTraceRead(offset,limit,generation)
 return '{"next":'..(offset+limit)..',"stale":false,"records":[],"padding":"'..string.rep('y',3000)..'"}'
end
for i=31,100 do
 local r={player=1,city=7,district=8,plot=i,quarter='BAKERS',production=0,gold=2,total=2,materialOnSite=false,legal=true}
 snapshot.candidates[#snapshot.candidates+1]=r
end
turn=2;CSC_AI_CEPolicy.Refresh('large-receipts')
''')
        lines=to_python(l.globals().receipts)
        self.assertTrue(any('CSC_CE_POLICY_CHUNK='in line for line in lines))
        self.assertTrue(all(len(('CSC_CE_Policy: '+line).encode('utf-8'))<2047 for line in lines))
        rows=logical_receipts(lines)
        scan=next(v for k,v in reversed(rows)if k=='SCAN')
        plan=next(v for k,v in reversed(rows)if k=='PLAN')
        native=next(v for k,v in reversed(rows)if k=='NATIVE')
        trace=next(v for k,v in reversed(rows)if k=='TRACE')
        self.assertEqual(scan['unicode'],'é水\n'*1000)
        self.assertEqual(len(plan['entries']),71)
        self.assertEqual(native['status']['longField'],'x'*2500)
        self.assertEqual(trace['page']['padding'],'y'*3000)
        self.assertFalse(l.eval('CSC_CE_PolicyStatus().failed'))
    def test_missing_duplicate_or_corrupt_receipt_chunk_is_rejected(self):
        l=self.make('snapshot.padding=string.rep("x",3000)')
        frames=[line for line in to_python(l.globals().receipts)if 'CSC_CE_POLICY_CHUNK='in line]
        self.assertTrue(frames)
        for damaged in (frames[:-1],frames[:1]+frames,frames[:-1]+[frames[-1].replace('7878','7879',1)]):
            with self.assertRaises(ValueError):logical_receipts(damaged)

class PackageTests(unittest.TestCase):
    def test_isolated_dependency_pins_the_actual_imported_core(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            dependency = directory / 'test-copy-core.lua'
            dependency.write_text('-- distinct dependency bytes\n', encoding='utf-8')
            selected = 'd0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a08'
            result = BUILDER.build(directory / 'package-build', csc_id=selected,
                                   adjacency_core=dependency)
            mod = ET.parse(Path(result['package']) / 'CSC_CE_Policy.modinfo').getroot()
            dependencies = {x.attrib['id'] for x in mod.findall('Dependencies/Mod')}
            self.assertIn(selected, dependencies)
            self.assertNotIn(BUILDER.CSC_ID, dependencies)
            receipt = json.loads(Path(result['manifest']).read_text(encoding='utf-8'))
            pin = receipt['adjacency_core_from_dependency']
            self.assertEqual(pin['source'], str(dependency.resolve()))
            self.assertEqual(pin['sha256'], BUILDER.sha(dependency))
            self.assertFalse(list(Path(result['package']).rglob('*AdjacencyCore*')))

    def test_lua_only_package_reuses_scanner_bytes_and_declares_dependencies(self):
        with tempfile.TemporaryDirectory()as directory:
            result=BUILDER.build(Path(directory)/'package-build')
            package=Path(result['package']);self.assertEqual(result['context'],'CSC_CE_Policy')
            self.assertEqual((package/'Lua/CSC_AI_AdjacencyScan.lua').read_bytes(),
                (ROOT/'Civ Supply Chains/Lua_UI/AI/CSC_AI_AdjacencyScan.lua').read_bytes())
            self.assertFalse(list(package.rglob('*.dll')))
            mod=ET.parse(package/'CSC_CE_Policy.modinfo').getroot()
            self.assertEqual({x.attrib['id']for x in mod.findall('Dependencies/Mod')},
                {BUILDER.CE_FORK_ID,BUILDER.CSC_ID,BUILDER.GS_ID})
            self.assertEqual(mod.find('InGameActions/AddGameplayScripts/File').text,'Lua/CSC_CE_Policy.lua')
            self.assertNotIn('CSC_AdjacencyGameplay',GAMEPLAY_SOURCE)

if __name__=='__main__':unittest.main()
