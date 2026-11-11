"""Seal the first matched river window; this script writes no live policy.

Replay logs contain immutable CE trace prefixes with stable generation/index
keys. Join native input/result rows to ordinary packet counts, retain the full
set of differences and inspect actual winners. A successful file/packet audit
alone is not a placement closure: Astra must review the native choice and scope.
"""
import argparse
import json
from pathlib import Path
import re
from driver import load,read,sha,write_json
from liverpool_river_policy import without_river

TARGET=(4,131073,36,2497)


def collect(folder):
    assert load(folder/'complete.json')['verified']
    assert load(folder/'session-closed.json')['verified']
    text=read(folder/'Lua.log')
    assert 'CSC_HOST_DIAG_FAILED' not in text
    assert 'CSC_AI_BAKERS_DISTRICTS_FAILED' not in text
    assert 'CSC_AI_INDUSTRY_PLACEMENT_FAILED' not in text
    records={}
    for turn,generation,index,raw in re.findall(r'CSC_HOST_NATIVE\s+(\d+)\s+(\d+)\s+(\d+)\s+(\{[^\r\n]+\})',text):
        row=json.loads(raw);key=(int(generation),int(index))
        assert row['generation']==key[0]
        assert key not in records or records[key]==row,'Repeated prefix changed an indexed record'
        records[key]=row
    begin=re.findall(r'CSC_HOST_PREFIX_BEGIN\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',text)
    end=re.findall(r'CSC_HOST_PREFIX_END\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',text)
    assert begin==end,'Native trace prefix did not complete'
    packets={int(version):dict(turn=int(turn),count=int(count),omitted=int(omitted))
        for turn,version,count,omitted in re.findall(
            r'CSC_AI_BAKERS_DISTRICTS turn=(\d+) version=(\d+) players=\d+ entries=(\d+) omitted=(\d+)',text)}
    assert packets and records
    first=min(packets)
    assert packets[first]['turn']==25 and packets[first]['omitted']==0
    nets={}
    for row in records.values():
        if row['version']!=first or row['k']!='net':continue
        key=tuple(row[k]for k in ('player','city','district','plot'))
        assert key not in nets or nets[key]==row,'Multiple unequal first-window inputs for a pair'
        nets[key]=row
        assert row['eligible']==1 and row['reason']==0
    assert len(nets)==packets[first]['count'],'Trace does not cover the complete published first packet'
    caches={}
    for row in records.values():
        if row['version']!=first or row['k']!='cache':continue
        key=tuple(row[k]for k in ('player','city','district','plot'))
        assert key not in caches or caches[key]==row,'Multiple unequal first-window caches for a pair'
        caches[key]=row
    assert caches.keys()==nets.keys(),'Published pair has no cache read or an unexpected pair was retained'
    offers=re.findall(r'CSC_EARLY_RETAINED_OFFER\s+25\s+'+str(first)+
        r'\s+4\s+131073\s+36\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\d+)',text)
    assert offers
    other_arrays={}
    for name,pattern in (
        ('builders',r'CSC_AI_BAKERS_BUILDERS turn=25 allowances=(\d+)'),
        ('nominations',r'CSC_AI_BAKERS_NOMINATIONS turn=25 bids=(\d+)'),
        ('repairs',r'CSC_AI_BAKERS_REPAIRS turn=25 candidates=(\d+)'),
        ('exclusions',r'CSC_AI_SUPPLIER_EXCLUSIONS turn=25 sites=(\d+) omitted=0'),
        ('customer_sites',r'CSC_AI_BAKERS_PLACEMENT turn=25 bids=\d+ weak=\d+ customer=(\d+)')):
        values=re.findall(pattern,text)
        assert len(values)==1 and values[0]=='0','Other policy array needs explicit attribution: '+name
        other_arrays[name]=0
    winners=[row for row in records.values()if row['version']==first and row['k']=='best'
        and (row['player'],row['city'])==TARGET[:2]]
    return dict(inputs=load(folder/'inputs.json'),packets=packets,nets=nets,
        records=list(records.values()),winners=winners,first=first,other_arrays=other_arrays,
        caches=caches,retained_city_offers=offers,
        inspection=load(folder/'cases/boston-selection/liverpool-inspection.json'))


def audit(full,control):
    a,b=collect(full),collect(control)
    assert a['inputs']['saves']==b['inputs']['saves']
    assert a['inputs']['packages'].keys()==b['inputs']['packages'].keys()
    differences=[]
    for package,files in a['inputs']['packages'].items():
        other=b['inputs']['packages'][package]
        assert files.keys()==other.keys()
        differences.extend((package,path)for path,value in files.items()if value!=other[path])
    assert len(differences)==1 and differences[0][1].replace('\\','/')=='Lua_UI/AI/CSC_AI_AdjacencyScan.lua'
    assert without_river((full/'CSC_AI_AdjacencyScan.lua').read_bytes())==(control/'CSC_AI_AdjacencyScan.lua').read_bytes()
    common=a['nets'].keys()&b['nets'].keys()
    assert all(a['nets'][key]['base']==b['nets'][key]['base']for key in common),'Shared native input baselines differ'
    # Withholding the river can move the one owned-site promotion to another
    # candidate. Do not demand the hypothesised +24 at the original plot or
    # pretend CE observed the raw baseline of an unpublished pair. Absence is
    # zero CSC delta; native score/eligibility at that missing pair is unknown.
    for field in ('baseRule','supply','plots','riverEdges','site','futureHost','originalRoles'):
        assert a['inspection'][field]==b['inspection'][field],'Physical source facts differ: '+field
    assert a['inspection']['forecast']['total']==4 and b['inspection']['forecast']['total']==3
    packet_differences=[]
    for key in sorted(a['nets'].keys()|b['nets'].keys()):
        left,right=a['nets'].get(key),b['nets'].get(key)
        delta_a=left['result']-left['base']if left else 0
        delta_b=right['result']-right['base']if right else 0
        if delta_a!=delta_b:packet_differences.append(dict(key=key,full_delta=delta_a,control_delta=delta_b,
            full_native_record=left,control_native_record=right))
    assert [(r['key'],r['full_delta'],r['control_delta'])for r in packet_differences]==[
        (TARGET,12288,0),((4,131073,36,2571),0,12288)],'Unexpected additional policy difference'
    assert len(a['winners'])==len(b['winners'])==1,'Expected one fresh native city comparison'
    winner=lambda row:(row['district'],row['plot'])
    for arm in (a,b):
        row=arm['winners'][0]
        key=tuple(row[k]for k in ('player','city','district','plot'))
        assert arm['nets'][key]['result']==arm['caches'][key]['result']==row['result']
    cache_differences=[dict(key=key,full=a['caches'][key]['result'],control=b['caches'][key]['result'])
        for key in sorted(common)if a['caches'][key]['result']!=b['caches'][key]['result']]
    return dict(artifact_audit_verified=True,closure_claim=False,
        scope='Problem1.3 prospective Water Mill river input; not realised yield or construction',
        source=a['inputs']['saves'],manifest_differences=differences,
        first_window_versions=dict(full=a['first'],control=b['first']),
        complete_packet_counts=dict(full=len(a['nets']),control=len(b['nets'])),
        common_native_pair_count=len(common),common_native_baselines_equal=True,
        packet_differences=packet_differences,common_cache_differences=cache_differences,
        unpaired_native_baseline_limit='CE records published pairs; each promoted site has no raw counterpart record in the other arm',
        retained_city_offers=dict(full=a['retained_city_offers'],control=b['retained_city_offers']),
        other_arrays_identical_zero=a['other_arrays']==b['other_arrays'],
        promoted_winners_match_net_and_cache=True,
        winners=dict(full=a['winners'][0],control=b['winners'][0]),
        native_choice_changed=winner(a['winners'][0])!=winner(b['winners'][0]),
        pins={name:{file:sha(folder/file)for file in ('inputs.json','Lua.log','AI_CityBuild.csv',
            'AI_Behavior_Trees.csv','City_BuildQueue.csv','complete.json','session-closed.json')}
            for name,folder in (('full',full),('control',control))})


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--full',type=Path,required=True);p.add_argument('--control',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();assert not args.output.exists(),'Never replace an evidence audit'
    result=audit(args.full,args.control);write_json(args.output,result)
    print(json.dumps(result,ensure_ascii=True))
