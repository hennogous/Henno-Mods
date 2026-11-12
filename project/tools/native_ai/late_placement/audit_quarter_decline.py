"""Seal the causal deferral half of1.7; never claim later reconsideration.

Only archived files are read. The exact post-selector matrix, physical facts,
numeric offers and package contents must match. The sole ablation removes
one city's Bakers admission scopes. Actual native winners and requests supply
the outcome; counters or a competing cache value alone cannot pass this audit.
"""
import argparse
import json
from pathlib import Path
import re
from driver import load,read,sha,manifest,write_json

CITY=(1,524295)


def collect(folder,arm):
    assert load(folder/'complete.json')['verified'] and load(folder/'session-closed.json')['verified']
    inputs=load(folder/'inputs.json');assert inputs['deferral_arm']==arm
    for package,pin in inputs['packages'].items():assert manifest(folder/package)==pin
    text=read(folder/'Lua.log')
    assert not any(s in text for s in ('CSC_HOST_DIAG_FAILED','CSC_AI_BAKERS_DISTRICTS_FAILED','CSC_AI_INDUSTRY_PLACEMENT_FAILED'))
    assert re.findall(r'CSC_HOST_PREFIX_BEGIN\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',text)==re.findall(
        r'CSC_HOST_PREFIX_END\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',text)
    records={}
    for t,g,i,raw in re.findall(r'CSC_HOST_NATIVE\s+(\d+)\s+(\d+)\s+(\d+)\s+(\{[^\r\n]+\})',text):
        row=json.loads(raw);key=(int(g),int(i))
        assert key not in records or records[key]==row
        records[key]=row
    trace=load(folder/'selector-trace.json');assert trace['fault']is None and trace['active']==0
    selection,=[r for r in trace['records']if r['kind']=='selection'];assert selection['turn']==203
    assert len(selection['sites'])==36 and all(len(s['scoresQ8'])==38 for s in selection['sites'])
    # Packet observations label the publication. They are proposed metadata,
    # joined below to the actual versioned native consumption and comparison.
    facts=[line for line in re.findall(r'CSC_DEFERRAL_SITE_FACTS[^\r\n]+',text)if line.split()[1:3]==['203','4']]
    offers=[line for line in re.findall(r'CSC_DEFERRAL_RETAINED[^\r\n]+',text)if line.split()[1:3]==['203','4']]
    assert len(facts)==36 and len(offers)==11
    assert re.search(r'CSC_DEFERRAL_BASE_VISIBILITY\s+203\s+4\s+true',text)
    assert 'DISTRICT_HIPPODROME\tDISTRICT_CSC_BAKERS_QUARTER\tDISTRICT_CSC_TAILORS_QUARTER' in text
    target=[r for r in records.values()if r['version']==4 and(r['player'],r['city'])==CITY]
    nets={r['plot']:r for r in target if r['k']=='net'and r['district']==36}
    masks={r['plot']:r for r in target if r['k']=='decline'and r['district']==36}
    best,=[r for r in target if r['k']=='best']
    assert len(nets)==11 and all(r['reason']==0 and r['eligible']==1 and r['result']-r['base']==-65536 for r in nets.values())
    rows={r['plot']:r for r in selection['sites']}
    for plot,net in nets.items():assert rows[plot]['q8']==net['result']
    if arm=='full':
        assert masks.keys()==nets.keys()
        for plot,mask in masks.items():
            assert mask['reason']==0 and mask['eligible']==1 and mask['base']==nets[plot]['result']
            assert mask['result']==-9999*256-1
    else:assert not masks
    requests=[line for line in read(folder/'AI_CityBuild.csv').splitlines()
        if line.startswith('203, 1, LOC_CITY_NAME_NICOPOLIS,')and ', SUBMITTED,'in line
        and ', Build City District'in line]
    request,=requests
    expected='DISTRICT_HIPPODROME'if arm=='full'else'DISTRICT_CSC_BAKERS_QUARTER'
    assert expected in request and 'CONTRACT 4333,'in request
    assert expected+': Accepted at 'in read(folder/'AI_Behavior_Trees.csv')
    return dict(inputs=inputs,records=records,selection=selection,facts=facts,offers=offers,
        nets=nets,masks=masks,best=best,request=request)


def audit(full,control):
    a,b=collect(full,'full'),collect(control,'control')
    assert a['inputs']['save_sha256']==b['inputs']['save_sha256']
    assert a['inputs']['ce_sha256']==b['inputs']['ce_sha256']== \
        'a849eff803d68f7dc4061421c98812ae466b50f0d96a790f884f0f7bcf60eafb'
    differences=[]
    for package,files in a['inputs']['packages'].items():
        other=b['inputs']['packages'][package];assert files.keys()==other.keys()
        differences.extend((package,path)for path,value in files.items()if value!=other[path])
    assert differences==[('CSC Bakers Development Mod','Lua_UI\\AI\\CSC_AI_BakersGameplay.lua')]
    # Reconstruct both diagnostic copies from the same shipping publisher.
    # This also prevents an unnoticed second policy writer in the ablation.
    from host_choice_policy import stage as reader
    from nicopolis_deferral_policy import stage
    source=Path('Civ Supply Chains/Lua_UI/AI/CSC_AI_BakersGameplay.lua').read_bytes()
    for folder,arm in ((full,'full'),(control,'control')):
        assert (folder/'CSC_AI_BakersGameplay.lua').read_bytes()==reader(stage(source,arm=arm),[],start=200,end=204,players=[1])
    assert a['facts']==b['facts'] and a['offers']==b['offers'] and a['nets']==b['nets']
    physical={int(f[3]):f for line in a['facts']if(f:=line.split())}
    for plot in a['nets']:
        facts=physical[plot]
        assert facts[7:11]==['true','true','false','false'] # legal, revealed, no uncertainty/potential.
    assert a['selection']['sites']==b['selection']['sites'],'Any matrix or native flag difference needs separate attribution'
    assert a['selection']['winner']==dict(district=31,x=28,y=6,q8=306049)
    assert b['selection']['winner']==dict(district=36,x=28,y=6,q8=347924)
    assert (a['best']['district'],a['best']['plot'],a['best']['result'])==(31,472,306049)
    assert (b['best']['district'],b['best']['plot'],b['best']['result'])==(36,472,347924)
    for line in a['offers']:
        fields=line.split();assert fields[5]=='true'and fields[6]=='0'and fields[8]=='true'
    return dict(verified_deferral_half=True,whole_1_7_complete=False,
        full=str(full),control=str(control),source_sha256=a['inputs']['save_sha256'],ce_sha256=a['inputs']['ce_sha256'],
        package_file_differences=differences,all_archived_packages_rehashed=True,
        exact_equal_matrix=dict(rows=36,columns=38,flags_and_reservations=True),
        identical_numeric_bakers_inputs=11,temporary_declines=11,
        full_choice=a['selection']['winner'],control_choice=b['selection']['winner'],
        full_request=a['request'],control_request=b['request'],native_masks=list(a['masks'].values()),
        hashes={str(p):sha(p)for folder in(full,control)for p in(folder/'Lua.log',folder/'selector-trace.json',folder/'inputs.json')},
        remaining='Credible new Base opportunity, dynamic scope withdrawal and a fresh Quarter choice/request in continued treatment.',
        limits='Representative controlled knowledge fixture. No construction, realised Service or broader qualification claim. Astra review required.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for key in('full','control','output'):parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args();result=audit(args.full,args.control);write_json(args.output,result)
    print('Verified native deferral comparison; reconsideration remains open.')
