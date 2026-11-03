"""Offline matched native-rule comparison; never opens or controls Civilization."""
import argparse,collections,hashlib,importlib.util,json,re,sys
from pathlib import Path
from material_forecast_contract import source_parity
from material_checkpoint_logs import reconstruct_checkpoint
from log_intelligence import records
from material_decision_intelligence import reservations
from material_boost_activity import report as activity_report
from material_boost_log import report as boost_report
from material_job_origin_intelligence import report as origin_report

import material_rejected_work_intelligence as rejected_work
LABELS=('control','native_rule')
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def loss_union(audits):
    found={}
    for label,audit in zip(LABELS,audits):
        for row in audit['loss_attribution']['cases']:
            key=(row['plot'],row.get('prior_resource'))
            entry=found.setdefault(key,dict(plot=key[0],resource=key[1],losses={}))
            entry['losses'].setdefault(label,[]).append(row)
    return sorted(found.values(),key=lambda x:(x['plot'],str(x['resource'])))

def endpoint_state(plot,resource,sites,scope):
    retained=(plot.get('resource')==resource)if plot is not None and resource is not None else None
    links=[]
    for ref in scope:
        site=next((s for s in sites if(s['plot'],s['quarter'])==(ref['plot'],ref['quarter'])),None)
        material=next((m for m in site['materials']if(m['plot'],m['resource'],m['category'])==(ref['material_plot'],resource,ref['category'])),None)if site else None
        owned=bool(material and material['owner']==site['player'])
        working=bool(owned and material.get('improvement')and not material.get('pillaged',False))
        functioning=bool(working and site['complete']and not site['pillaged']and site['producer_built'])
        links.append(dict(**ref,Quarter_present=site is not None,current_Quarter_owner=site['player']if site else None,owned_material=owned,working_improvement_proxy=working,functioning_producer_proxy=functioning,producer_built=site['producer_built']if site else None,Quarter_complete=site['complete']if site else None,Quarter_pillaged=site['pillaged']if site else None))
    return dict(endpoint_plot_observed=plot is not None,resource_identity_known=resource is not None,resource_present=retained,owner=plot.get('owner')if plot else None,improvement=plot.get('improvement')if plot else None,pillaged=plot.get('pillaged')if plot else None,district=plot.get('district')if plot else None,links=links,working_links=sum(x['working_improvement_proxy']for x in links),functioning_links=sum(x['functioning_producer_proxy']for x in links),retention_between_checkpoints_proven=False)

def reference_scope(index,resource,all_points,source):
    found={};source_tiles=[t for c in source['production']['cities']for t in c['tiles']if t['index']==index]
    if source_tiles:
        first=source_tiles[0]
        for tile in source_tiles[1:]:
            assert tile['resource']==first['resource']and set(tile['neighbors'])==set(first['neighbors'])and tile['base_for']==first['base_for']and tile['spec_for']==first['spec_for'],'Conflicting source resource mapping'
    else:first=None
    for point in all_points:
        for site in point['sites']:
            categories={m['category']for m in site['materials']if m['plot']==index and m['resource']==resource}
            if first and site['plot']in first['neighbors']:
                if site['quarter']in first['base_for']:categories.add('base')
                if site['quarter']in first['spec_for']:categories.add('spec')
            for category in categories:
                assert category in('base','spec'),'Unknown material category'
                key=(site['plot'],site['quarter'],category)
                found[key]=dict(plot=site['plot'],quarter=site['quarter'],category=category,material_plot=index)
    return [found[k]for k in sorted(found)]

def failure_routes(root,turn,width):
    text,coverage=reconstruct_checkpoint(root,'AI_Behavior_Trees.csv',turn)
    target={};intent={};routes={}
    for t,p,row,raw in records(text,16,turn,set(range(1,6))):
        if len(row)<7:continue
        key=(t,p,row[2],row[3]);result,node=row[4],row[5]
        if node=='Decode Trigger':
            match=re.search(r'Improve: (IMPROVEMENT_[A-Z0-9_]+); Value: ([0-9.]+)',raw)
            intent[key]=match[1]if match else None
        if node=='Reserve Plot':
            match=re.search(r'Reserving plot (-?\d+) (-?\d+)',raw)
            target[key]=int(match[2])*width+int(match[1])if match and result in('SUCCESS','READY','RUNNING')and int(match[1])>=0 and int(match[2])>=0 else None
        if result not in('FAILURE','FAILED')or target.get(key)is None:continue
        identity=(p,row[2],row[3],target[key],node,intent.get(key))
        found=routes.setdefault(identity,dict(player=p,system=row[2],tree=row[3],plot=target[key],node=node,planned_improvement=intent.get(key),first_observed_turn=t,last_observed_turn=t,failure_records=0,example=raw))
        found['last_observed_turn']=t;found['failure_records']+=1
    return dict(routes=list(routes.values()),coverage=coverage,scope='Failure records with a same-turn logged reserved plot. Distinct route identities are not persistent job IDs or proof that harvest caused failure.')

def compare(control,rule):
    roots=(Path(control),Path(rule));audits=[read(r/'independent-diagnostic-audit.json')for r in roots]
    assert all(a['verified']and a['endpoint']==75 and a['arm']=='raw-resource'and a['runtime_restored510']and a['new_worlds']==0 for a in audits),'Both independent complete75 audits required'
    assert audits[1]['runtime_harvest_rule']and audits[1]['measured_rule_legality']and audits[1]['raw_control_audit_sha256']==sha(roots[0]/'independent-diagnostic-audit.json')
    assert audits[0]['source_sha256']==audits[1]['source_sha256']
    assert read(roots[0]/'native-database-inventory.json')==read(roots[1]/'native-database-inventory.json'),'Loaded DB differs: runtime-rule experiment only'
    sources=[read(r/'source16-initial.json')for r in roots];source_parity(sources[0],sources[1],{})
    primary=[read(r/'game-01/turn-075.json')for r in roots]
    points=[[read(r/'metric-points'/f'turn-{t:03d}.json')for t in(16,25,50,75)]for r in roots]
    all_points=[p for arm in points for p in arm];entries=loss_union(audits)
    source_plots={p['index']:p for p in sources[0]['world']['plots']}
    for index in(1573,2533,2269,1647,2563,1619,2489):
        resource=source_plots.get(index,{}).get('resource')
        if resource is not None and not any(e['plot']==index and e['resource']==resource for e in entries):entries.append(dict(plot=index,resource=resource,losses={},sentinel=True))
    focus=[]
    for entry in sorted(entries,key=lambda e:(e['plot'],str(e['resource']))):
        scope=reference_scope(entry['plot'],entry['resource'],all_points,sources[0]);states={};history={}
        for label,census,arm_points in zip(LABELS,primary,points):
            plot=next((p for p in census['plots']if p['index']==entry['plot']),None)
            states[label]=endpoint_state(plot,entry['resource'],arm_points[-1]['sites'],scope)
            history[label]=[dict(turn=p['turn'],observed_material_links=[dict(Quarter_plot=s['plot'],quarter=s['quarter'],owner=s['player'],complete=s['complete'],producer_built=s['producer_built'],material=m)for s in p['sites']for m in s['materials']if(m['plot'],m['resource'])==(entry['plot'],entry['resource'])])for p in arm_points]
        focus.append(dict(**entry,Quarter_reference_scope=scope,scope_description='Union of actually observed sites/material links and source16 adjacency/mapping; sparse observations do not establish continuous support.',states=states,checkpoint_links=history))
    activity=[activity_report(r,75)for r in roots];boosts=[boost_report(r,75)for r in roots];origins=[origin_report(r,75)for r in roots]
    failures=[failure_routes(r,75,primary[0]['width'])for r in roots]
    return dict(verified_pair=True,endpoint=75,source_sha256=audits[0]['source_sha256'],new_worlds=0,independent_world_samples=1,counterfactual_replay='One source16 world replayed16..75 in each trajectory; overlapping prefixes/outcomes never summed.',native_rule_definition='TRAIT_MAORI_PREVENT_HARVEST',native_rule_scope='All resource harvesting and associated placement legality for players1..5 only; observer0 excluded.',startup_legality_changes=read(roots[1]/'source-validation.json')['source_rule_legality_evidence'],source_DB_equal=True,counts=dict(zip(LABELS,[a['AI_counts']for a in audits])),economics={label:dict(funding=a['funding'],new_tiles=a['new_tile_acquisitions'],new_cost=a['new_gold_spent'],new_donations=a['new_donations'],foundations=a['foundations'])for label,a in zip(LABELS,audits)},loss_summaries={label:a['loss_attribution']['summary']for label,a in zip(LABELS,audits)},focus_cases=focus,repairs={label:a['repair_episodes']for label,a in zip(LABELS,audits)},boost_activity=dict(zip(LABELS,activity)),native_boost_records=dict(zip(LABELS,boosts)),harvest_job_origins=dict(zip(LABELS,origins)),failed_reserved_plot_routes=dict(zip(LABELS,failures)),native_rejected_work=dict(zip(LABELS,[rejected_work.report(r,75)for r in roots])),repair_summary={label:dict(completed_native_matched=sum(e.get('outcome')=='working'and e.get('native_repair_matched')is True for e in audit['repair_episodes']),pending=sum(e.get('outcome')=='pending_at_last_care_checkpoint'for e in audit['repair_episodes']),total_observed_episodes=len(audit['repair_episodes']))for label,audit in zip(LABELS,audits)},limits=['Rule is deliberately coarse; a retention benefit does not establish a safe targeted preservation implementation.','Raw private resource valuation affects human automatic citizen allocation in both arms; neither is AI-only release tuning or untreated baseline.','Improvement/producer link gates are structural working-supply proxies, not exact Service transaction or monetary payment evidence.','Missing endpoint plot or prior resource identity stays unknown; no harvest/destruction inferred from an absent observation.','Native source CanProduce may close because all owned locations became invalid; that is not necessarily a tech/civic lock.','Sparse checkpoint links cannot establish uninterrupted retention or exact loss/repair timing.','Observed failed routes do not establish persistent job identity or attribute failure to this rule without additional native evidence.','Different downstream worlds cannot isolate whole-mod causality or universal safety.'])

def markdown(v):
    lines=['# Existing native harvest rule: matched source16–75','','One saved-world counterfactual, both trajectories independently audited.','','| Metric | Raw control | Native rule |','|---|---:|---:|']
    for k,n in v['counts']['control'].items():lines.append(f'| {k} | {n} | {v["counts"]["native_rule"][k]} |')
    lines+=['','Loss classifications: `'+json.dumps(v['loss_summaries'])+'`.','','| Material plot | Resource | Present control/rule | Working links control/rule | Functioning producer links control/rule |','|---|---|---|---|---|']
    for c in v['focus_cases']:
        a,b=[c['states'][l]for l in LABELS]
        lines.append(f'| {c["plot"]} | {c["resource"]} | {a["resource_present"]} / {b["resource_present"]} | {a["working_links"]} / {b["working_links"]} | {a["functioning_links"]} / {b["functioning_links"]} |')
    lines+=['','Acquisition economics (full cost, own funds and fallback distinguished): `'+json.dumps(v['economics'])+'`.','','Native rejected-action paths, exact-plot development starts, failed reserved-plot routes and boost logs are preserved in JSON. Tree SUCCESS alone is not a native effect; short rejection loops can later resolve to valid improvements.','','Limits:']+['- '+x for x in v['limits']]
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('control',type=Path);p.add_argument('rule',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();v=compare(a.control,a.rule);a.output.mkdir(parents=True,exist_ok=True);(a.output/'comparison.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8');(a.output/'comparison.md').write_text(markdown(v),encoding='utf-8');print(json.dumps({k:v[k]for k in('verified_pair','counts','loss_summaries')}))
