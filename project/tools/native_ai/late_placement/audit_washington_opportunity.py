"""Seal1.7's remaining reconsideration leg; C165 separately proves deferral.

Read-only archived-file audit. A prior staged scope, ordinary withdrawal and
an actual supported Quarter choice/request are required. This cannot claim a
single uninterrupted city-level cycle, construction or realised Services.
"""
import argparse
import json
from pathlib import Path
import re
from driver import load,read,sha,manifest,write_json
from early_host_policy import stage as early
from host_choice_policy import stage as reader
from washington_opportunity import stage as opportunity


def audit(folder,policy):
    assert load(folder/'complete.json')['verified']
    assert load(folder/'session-closed.json')['verified']
    inputs=load(folder/'inputs.json')
    assert inputs['washington_opportunity'] and inputs['early_host_scout'] and inputs['early_endpoint']==24
    source,=inputs['saves'].values()
    assert source['turn']==22 and source['sha256']=='9675be27c614a2429a9cdca485a09a8d7421e627cc7833cb472bb9b1c390f55a'
    assert sha(Path(source['path']))==source['sha256']
    assert inputs['ce_sha256']=='a849eff803d68f7dc4061421c98812ae466b50f0d96a790f884f0f7bcf60eafb'
    count=0
    for name,pins in inputs['packages'].items():
        assert manifest(folder/name)==pins
        count+=len(pins)
    # Reconstruct the two declared diagnostic wrappers from shipping modules.
    # Extra metadata/logging and temporary resource facts are the only edits.
    ai=policy/'Lua_UI/AI'
    scanner,publisher=early((ai/'CSC_AI_AdjacencyScan.lua').read_bytes(),
        (ai/'CSC_AI_BakersGameplay.lua').read_bytes())
    publisher=reader(opportunity(publisher),[],start=22,end=24,players=[1,2,3,4,5])
    assert (folder/'CSC_AI_AdjacencyScan.lua').read_bytes()==scanner
    assert (folder/'CSC_AI_BakersGameplay.lua').read_bytes()==publisher
    for relative in('Lua_UI/AI/CSC_AI_QuarterPlacement.lua','Lua_UI/AI/CSC_AI_DistrictBridge.lua',
            'Lua_UI/Adjacencies/CSC_AdjacencyUI.lua'):
        assert (folder/Path(relative).name).read_bytes()==(policy/relative).read_bytes()
    text=read(folder/'Lua.log')
    assert not any(x in text for x in('CSC_HOST_DIAG_FAILED','CSC_AI_BAKERS_DISTRICTS_FAILED',
        'CSC_AI_INDUSTRY_PLACEMENT_FAILED','Runtime Error'))
    beginnings=re.findall(r'CSC_HOST_PREFIX_BEGIN\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',text)
    assert beginnings and beginnings==re.findall(r'CSC_HOST_PREFIX_END\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',text)
    assert len(re.findall(r'CSC_WASH_BASE_ABSENT\s+22\s+796\s+1',text))==1
    assert len(re.findall(r'CSC_WASH_BASE_RESTORED\s+22\s+796\s+1\s+1\s+2',text))==1
    prior,=re.findall(r'CSC_WASH_PRIOR_SCOPE\s+22\s+1\s+(\{[^\r\n]+\})',text)
    assert json.loads(prior)['staged']==1
    # Resource restored at22, prior publication unchanged; ordinary23 writesv2.
    assert re.search(r'CSC_WASH_STATE\s+22\s+1\s+2\s+1\s+1\s+1',text)
    assert re.search(r'CSC_WASH_STATE\s+23\s+1\s+2\s+1\s+1\s+1',text)
    assert re.search(r'CSC_WASH_SUPPLIER\s+23\s+1\s+796\s+RESOURCE_CATTLE\s+true\s+false',text)
    assert re.search(r'CSC_AI_BAKERS_DISTRICTS turn=23 version=2 players=5 ',text)
    retired,=re.findall(r'CSC_WASH_DECLINE\s+24\s+2\s+(\{[^\r\n]+\})',text)
    assert json.loads(retired)['staged']==0
    records={}
    for t,g,i,raw in re.findall(r'CSC_HOST_NATIVE\s+(\d+)\s+(\d+)\s+(\d+)\s+(\{[^\r\n]+\})',text):
        row=json.loads(raw);key=(int(g),int(i))
        assert key not in records or records[key]==row
        assert any(int(bt)==int(t) and int(bg)==int(g) and int(i)<int(n)for bt,bg,v,n in beginnings)
        records[key]=row
    target=[r for r in records.values()if r['version']==2 and
        (r['player'],r['city'],r['district'],r['plot'])==(3,65536,36,870)]
    best,=[r for r in target if r['k']=='best']
    assert best['reason']==0 and best['eligible']==1 and best['result']==46411
    net,=[r for r in target if r['k']=='net']
    assert net['base']==40267 and net['result']==46411 and net['result']-net['base']==6144
    assert any(r['k']=='cache'and r['result']==46411 for r in target)
    request,=[line for line in read(folder/'AI_CityBuild.csv').splitlines()
        if line.startswith('23, 3, LOC_CITY_NAME_WASHINGTON,') and ', SUBMITTED,'in line
        and ', DISTRICT_CSC_BAKERS_QUARTER,'in line and line.endswith('Build City District')]
    assert 'CONTRACT 241,'in request
    journal=[json.loads(line)for line in read(folder/'controller-journal.ndjson').splitlines()]
    restored=[r for r in journal if r.get('label')=='restore-washington-base']
    assert len(restored)==2 and restored[0]['sent_at_most_once'] and restored[1]['acknowledged']
    helper=folder/'washington_opportunity.py'
    assert helper.read_bytes()==Path(__file__).with_name(helper.name).read_bytes()
    files=[folder/n for n in('inputs.json','Lua.log','AI_CityBuild.csv','controller-journal.ndjson',
        'complete.json','session-closed.json','washington_opportunity.py')]
    return dict(verified_reconsideration_leg=True,astra_review_required=True,
        composite_deferral_evidence='AI-C165',single_city_uninterrupted_cycle=False,
        folder=str(folder),source_sha256=source['sha256'],ce_sha256=inputs['ce_sha256'],
        package_files_rehashed=count,all_main_modules_reconstructed=True,
        prior_scope=json.loads(prior),retired_scope=json.loads(retired),
        ordinary_withdrawal_publication=dict(turn=23,version=2),native_net=net,native_best=best,
        actual_request=request,prefix_count=len(beginnings),unique_native_records=len(records),
        hashes={str(p):sha(p)for p in files},
        limits='Existing Cattle temporarily absent then exactly restored. No native acquisition, Quarter construction or Service claim.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for key in('folder','policy','output'):parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args();result=audit(args.folder,args.policy);write_json(args.output,result)
    print('Verified ordinary withdrawal, native Bakers870 choice and request241.')
