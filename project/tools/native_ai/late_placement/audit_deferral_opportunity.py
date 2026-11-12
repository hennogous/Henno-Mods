"""Audit a terminal1.7 continuation without turning a negative into closure.

This reads archived files only. The original matched audit proves causal
deferral; this continuation checks changed live supply, ordinary withdrawal
and any later exact native Quarter request. No game command is issued here.
"""
import argparse
import json
from pathlib import Path
import re

from driver import load,read,sha,manifest,write_json
from deferral_opportunity import qualify_before,qualify_after,quarter_request_after
from host_choice_policy import stage as reader
from nicopolis_deferral_policy import stage


def audit(folder,policy):
    complete=load(folder/'complete.json');assert complete['verified']
    assert load(folder/'session-closed.json')['verified']
    inputs=load(folder/'inputs.json')
    assert inputs['mode']=='integrated' and inputs['deferral_opportunity'] and inputs['deferral_arm']=='full'
    assert inputs['save_sha256']=='e333251ec7318fb6b170678a956c28e02e2f9b01c4c4753c99e84b1a112fe19a'
    assert inputs['ce_sha256']=='a849eff803d68f7dc4061421c98812ae466b50f0d96a790f884f0f7bcf60eafb'
    for name,pins in inputs['packages'].items():assert manifest(folder/name)==pins
    # Reconstruct the sole diagnostic publisher from shipping policy. Other
    # main AI files must be byte-identical; a second policy writer cannot pass.
    keys=[dict(player=1,city=524295,district=36,plot=p)for p in(397,398,472)]
    publisher=policy/'Lua_UI/AI/CSC_AI_BakersGameplay.lua'
    expected=reader(stage(publisher.read_bytes(),arm='full',opportunity=True),keys,
        start=200,end=inputs['through'],window_limit=54)
    assert (folder/publisher.name).read_bytes()==expected
    for relative in('Lua_UI/AI/CSC_AI_AdjacencyScan.lua','Lua_UI/AI/CSC_AI_QuarterPlacement.lua',
            'Lua_UI/AI/CSC_AI_DistrictBridge.lua','Lua_UI/Adjacencies/CSC_AdjacencyUI.lua'):
        assert (folder/Path(relative).name).read_bytes()==(policy/relative).read_bytes()
    initial=load(folder/'before-opportunity-selector.json')
    assert initial['fault']is None and initial['active']==0
    selected,=[r for r in initial['records']if r['kind']=='selection']
    assert selected['turn']==203 and selected['winner']==dict(district=31,x=28,y=6,q8=306049)
    before=load(folder/'before-opportunity.json');after=load(folder/'after-opportunity.json')
    qualify_before(before);supported=qualify_after(before,after)
    assert before['ceStatus']==after['ceStatus'],'Fixture forced a publication'
    assert before['city']==after['city']
    changed={k for k in before['supplier']if before['supplier'][k]!=after['supplier'][k]}
    assert changed=={'owner','city'}
    journal=[json.loads(line)for line in read(folder/'controller-journal.ndjson').splitlines()]
    mutation=[r for r in journal if r.get('label')=='transfer-diagnostic-base-opportunity']
    assert len(mutation)==2 and mutation[0]['event']=='command-begin' and mutation[0]['sent_at_most_once']
    assert mutation[1]['event']=='command-end' and mutation[1]['acknowledged']
    text=read(folder/'Lua.log')
    assert not any(s in text for s in('CSC_HOST_DIAG_FAILED','CSC_AI_BAKERS_DISTRICTS_FAILED','CSC_AI_INDUSTRY_PLACEMENT_FAILED'))
    assert re.findall(r'CSC_HOST_PREFIX_BEGIN\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',text)==re.findall(
        r'CSC_HOST_PREFIX_END\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',text)
    publications={int(v):int(t)for t,v in re.findall(r'CSC_AI_BAKERS_DISTRICTS turn=(\d+) version=(\d+)',text)}
    withdrawal={}
    for t,v,p,raw in re.findall(r'CSC_DEFERRAL_DECLINE_PREVIOUS\s+(\d+)\s+(\d+)\s+(\d+)\s+(\{[^\r\n]+\})',text):
        t,v,p=map(int,(t,v,p));receipt=json.loads(raw)
        if p in supported and publications.get(v,0)>204 and receipt['staged']==0:
            withdrawal.setdefault(p,dict(publication_turn=publications[v],version=v,read_turn=t,receipt=receipt))
    assert set(withdrawal)==set(supported),'No ordinary committed withdrawal for every supported site'
    trace=load(folder/'selector-trace.json');assert trace['fault']is None and trace['active']==0
    native={}
    for g,i,raw in re.findall(r'CSC_HOST_NATIVE\s+\d+\s+(\d+)\s+(\d+)\s+(\{[^\r\n]+\})',text):
        row=json.loads(raw);key=(int(g),int(i))
        assert key not in native or native[key]==row
        native[key]=row
    ledger=[]
    for selection in trace['records']:
        if selection['kind']!='selection':continue
        turn=selection['turn']
        rows=[r for r in native.values()if publications.get(r['version'])==turn]
        tracked=[]
        for site in selection['sites']:
            if site['plot']not in(397,398,472):continue
            observations=[r for r in rows if r['district']==36 and r['plot']==site['plot'] and r['k']in('net','cache')]
            # A neutral/omitted main pair has no matched CE Net/cache receipt.
            # Its matrix score is still directly observed by the selector;
            # do not invent a component split or demand a new probe for it.
            if observations:
                assert any(r['k']=='cache'and r['result']==site['q8']for r in observations),(turn,site['plot'],observations)
            tracked.append(dict(site=site,receipts=observations,component_split_available=bool(observations)))
        ledger.append(dict(turn=turn,winner=selection['winner'],tracked_bakers=tracked))
    outcome=quarter_request_after(read(folder/'AI_CityBuild.csv'),trace['records'],set(supported),text)
    recorded=load(folder/'reconsideration-outcome.json')
    assert recorded['outcome']==outcome and recorded['observed']==(outcome is not None)
    assert complete['actual_endpoint']==recorded['actual_endpoint']<=inputs['through']
    files=[folder/n for n in('inputs.json','before-opportunity.json','after-opportunity.json',
        'selector-trace.json','Lua.log','AI_CityBuild.csv','controller-journal.ndjson',
        'complete.json','session-closed.json','reconsideration-outcome.json')]
    return dict(verified_continuation=True,reconsideration_request_observed=outcome is not None,
        astra_review_required=True,folder=str(folder),source_sha256=inputs['save_sha256'],
        ce_sha256=inputs['ce_sha256'],all_archived_packages_rehashed=True,
        supported_sites=supported,sole_supplier_changes=sorted(changed),ordinary_withdrawal=withdrawal,
        native_score_ledger=ledger,
        actual_endpoint=complete['actual_endpoint'],outcome=outcome,
        hashes={str(p):sha(p)for p in files},
        limits='Controlled territorial opportunity, not native acquisition. No construction, Service or broad qualification claim.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for key in('folder','policy','output'):parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args();result=audit(args.folder,args.policy);write_json(args.output,result)
    print('Verified continuation; fresh Quarter request:',result['reconsideration_request_observed'])
