"""Offline comparison of the direct Pasture forecast arm; no native control."""
import argparse,hashlib,json,re,sqlite3,sys
from pathlib import Path
from material_forecast_contract import source_parity
from material_forecast_variants import declared_database_delta
from material_pasture_forecast import verify_loaded,verify_source,verify_final_snapshot
from material_native_rule_comparison import endpoint_state,reference_scope
from material_checkpoint_logs import reconstruct_checkpoint
from material_decision_intelligence import reservations
from material_rejected_work_intelligence import report as work_report
from material_boost_activity import report as activity_report
from material_boost_log import report as boost_report
from material_native_rule_checkpoint import checkpoint as closed_checkpoint

LABELS=('control','pasture_forecast')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def first_logged_plans(rows):
    rows=[r for r in rows if r.get('tree')=='Build City Improvement'and r.get('improvement')]
    if not rows:return dict(observed=False,turn=None,improvements=[],players=[],ambiguous=False,records=[],hidden_job_creation_time_proven=False)
    turn=min(r['turn']for r in rows);first=[r for r in rows if r['turn']==turn];improvements=sorted({r['improvement']for r in first});players=sorted({r['player']for r in first})
    return dict(observed=True,turn=turn,improvements=improvements,players=players,ambiguous=len(improvements)>1 or len(players)>1,records=first,hidden_job_creation_time_proven=False)

def plan_change(control,forecast):
    if not control['observed']or not forecast['observed']:return dict(comparison='UNOBSERVED',first_Farm_to_Pasture_observed=False,hidden_commitment_or_internal_utility_proven=False)
    eligible=not control['ambiguous']and not forecast['ambiguous']and control['players']==forecast['players']
    return dict(comparison='same first logged set'if control['improvements']==forecast['improvements']else'changed first logged set',first_Farm_to_Pasture_observed=eligible and control['improvements']==['IMPROVEMENT_FARM']and forecast['improvements']==['IMPROVEMENT_PASTURE'],hidden_commitment_or_internal_utility_proven=False)

def loss_union(audits):
    rows={}
    for label,audit in zip(LABELS,audits):
        for case in audit['loss_attribution']['cases']:
            key=(case['plot'],case.get('prior_resource'));row=rows.setdefault(key,dict(plot=key[0],resource=key[1],losses={}));row['losses'].setdefault(label,[]).append(case)
    return sorted(rows.values(),key=lambda x:(x['plot'],str(x['resource'])))

def supplemental_provenance(root):
    root=Path(root);v=read(root/'supplemental-import-provenance.json');assert v['verified']and v['worker_pins_file_not_edited']and v['helper_import_only']and v['activation_guard_OFF']
    assert sha(v['imported_helper'])==sha(v['source_snapshot'])==sha(v['identical_to_prelaunch_ended418_snapshot']['archive'])==v['sha256']
    commands=list((root/'pending-commands').glob('*.lua'));assert all('CSC_NATIVE_HARVEST_RULE.Begin('not in p.read_text(encoding='utf-8')for p in commands)
    assert not(root/'native-rule-activation.json').exists()
    return dict(verified=True,sha256=v['sha256'],commands_checked=len(commands),no_rule_activation_call=True,import_source_archive_equal=True)

def checkpoint_research(root,turn):
    root=Path(root);paths=list((root/'commands').glob('*-boundary-bundle-'+str(turn)+'.txt'));assert len(paths)==1,'Missing/ambiguous exact research export'
    text=paths[0].read_text(encoding='utf-8-sig');matches=re.findall(r'CSC_SERIES_RESEARCH=([^\r\n]+)',text);assert len(matches)==1,'Missing/ambiguous research packet'
    packet=json.loads(matches[0]);assert packet['turn']==turn and not packet['errors'],'Wrong/error research checkpoint'
    assert all(row['turn']<turn for row in packet['history']),'Research history extends beyond this inactive checkpoint'
    players={}
    for pid in range(1,6):
        history=[r for r in packet['history']if r['player']==pid]
        selected=[r['turn']for r in history if isinstance(r.get('tech'),dict)and r['tech'].get('value')=='TECH_APPRENTICESHIP']
        completions=[r for r in packet['completions']if r.get('player')==pid and r.get('item')=='TECH_APPRENTICESHIP']
        players[str(pid)]=dict(research_rows=len(history),first_observed_Apprenticeship_selection=min(selected,default=None),actual_Apprenticeship_completions=completions,Mining_seen_complete=any('TECH_MINING'in r.get('completed_techs',[])for r in history),AnimalHusbandry_seen_complete=any('TECH_ANIMAL_HUSBANDRY'in r.get('completed_techs',[])for r in history),Irrigation_seen_complete=any('TECH_IRRIGATION'in r.get('completed_techs',[])for r in history),actual_Irrigation_completions=[r for r in packet['completions']if r.get('player')==pid and r.get('item')=='TECH_IRRIGATION'])
    return dict(turn=turn,exact_export=str(paths[0]),export_sha256=sha(paths[0]),history_rows=len(packet['history']),players=players,scope='Exact archived boundary-bundle packet, never later research-latest rows or same-numbered future turns.')

def compare_checkpoint(control,forecast,turn):
    assert turn in(25,50),'Only declared intermediate checkpoints'
    control,forecast=Path(control),Path(forecast);audit=read(control/'independent-diagnostic-audit.json');startup=read(forecast/'independent-pasture-forecast-startup-confirmation.json');assert audit['verified']and audit['endpoint']==75 and startup['verified']and startup['harvest_rule_not_attached']
    assert audit['source_sha256']==read(forecast/'source-validation.json')['source_sha256']
    pins=read(forecast/'executed-source-pins.json');assert all(sha(p)==digest for p,digest in pins.items());extra=supplemental_provenance(forecast)
    roots=(control,forecast);values=[closed_checkpoint(r,turn)for r in roots];reserved=[];coverage=[]
    for root in roots:
        text,cov=reconstruct_checkpoint(root,'AI_Behavior_Trees.csv',turn);reserved.append(reservations(text,turn,74));coverage.append(cov)
    plans=[]
    for index in(1573,2533,2269,1647,2563,1619,2489):
        first={label:first_logged_plans([row for row in rows if row['plot']==index and 16<=row['turn']<=turn])for label,rows in zip(LABELS,reserved)}
        plans.append(dict(plot=index,first=first,comparison=plan_change(first['control'],first['pasture_forecast'])))
    return dict(midrun_checkpoint_report=True,final_independent_forecast75_audit_pending=True,through=turn,new_worlds=0,one_saved_world=True,pins_verified=len(pins),supplemental_import_provenance=extra,source_sha256=audit['source_sha256'],outcomes=dict(zip(LABELS,values)),first_logged_plans=plans,closed_log_boundaries=dict(zip(LABELS,coverage)),treatment_native_work=work_report(forecast,turn),research_checkpoints={label:checkpoint_research(root,turn)for label,root in zip(LABELS,roots)},limits=['Only the specified closed checkpoint, not final75 or universal effect.','First logged choice does not expose internal utility or hidden earlier queue commitments.','Tree SUCCESS is not native action proof; see native events, care transitions and physical outcomes.','Private signal affects all Pastures/humans; relative value and representation are not isolated.'])

def compare(control,forecast):
    roots=(Path(control),Path(forecast));audits=[read(r/'independent-diagnostic-audit.json')for r in roots]
    assert all(a['verified']and a['endpoint']==75 and a['arm']=='raw-resource'and a['runtime_restored510']and a['new_worlds']==0 for a in audits),'Both independently audited native75 trajectories required'
    assert audits[1]['branch']=='pasture-forecast-v5'and audits[1]['pasture_forecast_diagnostic']and not audits[1]['runtime_harvest_rule']and not audits[1]['measured_rule_legality']
    assert audits[1]['raw_control_audit_sha256']==sha(roots[0]/'independent-diagnostic-audit.json')and audits[0]['source_sha256']==audits[1]['source_sha256']
    initial=[read(r/'source16-initial.json')for r in roots];source_parity(initial[0],initial[1],{});verify_source(initial[1])
    base=read(roots[0].parent/'run-01/native-database-inventory.json');raw=read(roots[0]/'native-database-inventory.json');native=read(roots[1]/'native-database-inventory.json');delta=declared_database_delta(base,native,treatment=True,pasture_forecast=True,raw_control=raw)
    a=sqlite3.connect((roots[1]/'native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True);b=sqlite3.connect((roots[0]/'native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True)
    try:loaded=verify_loaded(a,b)
    finally:a.close();b.close()
    primary=[read(r/'game-01/turn-075.json')for r in roots];points=[[read(r/'metric-points'/f'turn-{t:03d}.json')for t in(16,25,50,75)]for r in roots];all_points=[p for arm in points for p in arm]
    private=verify_final_snapshot(read(roots[1]/'final-native-private-snapshot.json'),primary[1],read(roots[1]/'final-native-private-boundary.json'));assert private==read(roots[1]/'final-pasture-private-proof.json')
    extra=supplemental_provenance(roots[1]);entries=loss_union(audits);source_plots={p['index']:p for p in initial[0]['world']['plots']}
    for index in(1573,2533,2269,1647,2563,1619,2489):
        resource=source_plots.get(index,{}).get('resource')
        if resource is not None and not any(e['plot']==index and e['resource']==resource for e in entries):entries.append(dict(plot=index,resource=resource,losses={},sentinel=True))
    all_reserved=[];coverage=[]
    for root in roots:
        text,cov=reconstruct_checkpoint(root,'AI_Behavior_Trees.csv',75);all_reserved.append(reservations(text,75,primary[0]['width']));coverage.append(cov)
    cases=[]
    for entry in sorted(entries,key=lambda e:(e['plot'],str(e['resource']))):
        scope=reference_scope(entry['plot'],entry['resource'],all_points,initial[0]);states={};plans={}
        for label,census,arm_points,reserved in zip(LABELS,primary,points,all_reserved):
            plot=next((p for p in census['plots']if p['index']==entry['plot']),None);states[label]=endpoint_state(plot,entry['resource'],arm_points[-1]['sites'],scope)
            rows=[r for r in reserved if r['plot']==entry['plot']and 16<=r['turn']<=75];plans[label]=dict(first=first_logged_plans(rows),observed_reservation_records=rows)
        cases.append(dict(**entry,Quarter_scope=scope,states=states,plans=plans,plan_comparison=plan_change(plans['control']['first'],plans['pasture_forecast']['first'])))
    work=[work_report(r,75)for r in roots]
    return dict(verified_pair=True,source_sha256=audits[0]['source_sha256'],endpoint=75,new_worlds=0,independent_world_samples=1,counterfactual_replay='One source16 world replayed16..75 in each arm; shared prefix never summed.',native_table_delta_from_original512=delta,loaded_forecast=loaded,harvest_rule_off=True,supplemental_import_provenance=extra,final_native_Pasture_private_snapshot=private,raw_control_endpoint_private_yields='UNOBSERVED; do not substitute source16 values.',counts={label:a['AI_counts']for label,a in zip(LABELS,audits)},economics={label:dict(funding=a['funding'],new_tiles=a['new_tile_acquisitions'],new_cost=a['new_gold_spent'],new_donations=a['new_donations'],foundations=a['foundations'])for label,a in zip(LABELS,audits)},loss_summaries={label:a['loss_attribution']['summary']for label,a in zip(LABELS,audits)},focus_cases=cases,native_rejected_and_developed_work=dict(zip(LABELS,work)),repair_episodes={label:a['repair_episodes']for label,a in zip(LABELS,audits)},repair_summary={label:dict(completed_native_matched=sum(e.get('outcome')=='working'and e.get('native_repair_matched')is True for e in a['repair_episodes']),pending=sum(e.get('outcome')=='pending_at_last_care_checkpoint'for e in a['repair_episodes']))for label,a in zip(LABELS,audits)},boost_activity={label:activity_report(r,75)for label,r in zip(LABELS,roots)},native_boost_records={label:boost_report(r,75)for label,r in zip(LABELS,roots)},checkpoint_economics={label:[dict(turn=p['turn'],economic_yields=p['yields'],treasury_cashflow=p['treasury_cashflow'])for p in arm]for label,arm in zip(LABELS,points)},first_plan_log_coverage=dict(zip(LABELS,coverage)),research_checkpoints={label:[checkpoint_research(root,t)for t in(25,50,75)]for label,root in zip(LABELS,roots)},limits=['One broad private planning row, not a targeted AI-only release policy; all Pastures/human citizens may respond.','The treatment changes relative value and forecast representation; a response cannot isolate those components.','First logged plan is not hidden job creation time; multiple first-turn choices/players remain ambiguous.','No response alone proves neither engine disregard nor absence of preexisting hidden commitments.','A retained material is not working supply; improvement/ownership/producer and customer gates remain separate.','Final private yields are actual native observations, not isolated direct80 or a comparison with unobserved control endpoint values.','Tree SUCCESS is not a native effect; rejected log rows need not be unique requests or persistent jobs.','Sparse endpoints do not prove uninterrupted retention; actual Service monetary payments remain unobserved.'])

def markdown(v):
    lines=['# Direct Pasture forecast, matched source16-75','','Both trajectories independently audited; one saved world. Harvesting remains legal.','','| Metric | Raw control | Pasture forecast |','|---|---:|---:|']
    for k,x in v['counts']['control'].items():lines.append(f'| {k} | {x} | {v["counts"]["pasture_forecast"][k]} |')
    lines+=['','Observed losses: '+json.dumps(v['loss_summaries'])+'.','','| Plot | First logged control plan | First logged forecast plan | Resource retained control/forecast | Working links control/forecast |','|---|---|---|---|---|']
    for c in v['focus_cases']:
        p,q=[c['plans'][k]['first']for k in LABELS];a,b=[c['states'][k]for k in LABELS]
        lines.append(f'| {c["plot"]} | {p["turn"]}: {p["improvements"]} | {q["turn"]}: {q["improvements"]} | {a["resource_present"]}/{b["resource_present"]} | {a["working_links"]}/{b["working_links"]} |')
    lines+=['','Native development/rejection and first-plan raw records, repairs, boosts, exact finances and final native Pasture private yields are preserved in JSON. This is not an exact transaction ledger.','','Limits:']+['- '+x for x in v['limits']]
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('control',type=Path);p.add_argument('forecast',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--turn',type=int,choices=(25,50));a=p.parse_args();v=compare_checkpoint(a.control,a.forecast,a.turn)if a.turn else compare(a.control,a.forecast);a.output.mkdir(parents=True,exist_ok=True);(a.output/'comparison.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8');(a.output/'comparison.md').write_text(markdown(v)if not a.turn else '# Intermediate forecast checkpoint '+str(a.turn)+'\n\nFinal independent75 audit pending. See comparison.json for native outcome and plan evidence.\n',encoding='utf-8');print(json.dumps({k:v[k]for k in('verified_pair','counts','loss_summaries')}if not a.turn else dict(through=a.turn,counts={label:x['counts']for label,x in v['outcomes'].items()},first_Cattle2533=next(x for x in v['first_logged_plans']if x['plot']==2533))))
