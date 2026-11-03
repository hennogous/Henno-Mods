"""Offline three-trajectory comparison at closed native checkpoints; no game client.

New output code stays separate from the live worker and its frozen imports. A
checkpoint is not a final audit. Keep missing plots, prerequisites and planning
observations distinct from native effects and functioning producer supply.
"""
import argparse,collections,hashlib,json,sqlite3,sys
from pathlib import Path
from material_forecast_contract import source_parity
from material_resource_improvement_forecast import verify_loaded,verify_source,verify_final_snapshot
from material_pasture_forecast_comparison import first_logged_plans,checkpoint_research
from material_native_rule_checkpoint import checkpoint
from material_checkpoint_logs import reconstruct_checkpoint
from material_decision_intelligence import reservations
from material_rejected_work_intelligence import report as work_report
from material_care_audit import funding_gate
from full_game_controller.continuation import world_signature
from worker_allocation_contract import allocation_difference,channels_correspond

LABELS=('raw_control','pasture_only','resource_improvements')
SENTINELS=(1204,1573,1619,1647,1649,1794,2269,2489,2533,2563,2565,2751)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def material_rows(point,care,reserved,primary):
    """One owned material plot/player row; retain all supported Quarter links."""
    rows={};native={p['index']:p for p in primary['plots']}
    for site in point['sites']:
        for material in site['materials']:
            assert material['category']in('base','spec'),'Unknown material category'
            if material.get('owner')!=site['player']:continue
            key=(site['player'],material['plot'],material['resource'])
            row=rows.setdefault(key,dict(player=key[0],plot=key[1],resource=key[2],links=[],physical=native.get(key[1])))
            row['links'].append(dict(Quarter_plot=site['plot'],quarter=site['quarter'],category=material['category'],Quarter_complete=site['complete'],Quarter_pillaged=site['pillaged'],producer_built=site['producer_built'],material=material))
    for key,row in rows.items():
        states=[x for x in care['players'].get(str(row['player']),{}).get('plots',[])if x['plot']==row['plot']]
        assert len(states)<=1,'Ambiguous care state'
        row['care']=states[0]if states else None
        plans=[r for r in reserved if r['plot']==row['plot']and r['player']==row['player']]
        row['first_logged_city_improvement_plan']=first_logged_plans(plans)
        row['all_logged_reserved_plans']=plans
        row['care_state']=row['care']['state']if row['care']else 'UNOBSERVED'
        row['categories']=sorted({x['category']for x in row['links']})
        row['working_care_observed']=row['care_state']=='working'
        row['functioning_producer_link_count']=sum(x['Quarter_complete']and not x['Quarter_pillaged']and x['producer_built']and bool(x['material'].get('improvement'))and not x['material'].get('pillaged',False)for x in row['links'])
        row['no_logged_reserved_city_improvement_plan']=not row['first_logged_city_improvement_plan']['observed']
        row['no_logged_plan_is_no_hidden_job_claim']=False
    return sorted(rows.values(),key=lambda r:(r['player'],r['plot'],r['resource']))

def funding(root,turn):
    rows=[json.loads(line)for line in(root/'service-actions.ndjson').read_text(encoding='utf-8').splitlines()if line.strip()]
    begin=[x for x in rows if x['event']=='funded-acquisition-begin'and x['request']['turn']<=turn]
    closed=[x for x in rows if x['event']=='funded-acquisition-confirmed'and x['request']['turn']<=turn]
    assert len(closed)==len({x['request']['token']for x in closed})and {x['request']['token']for x in begin}=={x['request']['token']for x in closed},'Unclosed/duplicate economic effect at checkpoint'
    totals=funding_gate([(x['request'],x['receipt'])for x in closed])
    placed=[x for x in rows if x['event']=='foundation-confirmed'and x['turn']<=turn]
    return dict(**totals,foundations=placed,shared_pre16_tiles=sum(x['request']['turn']<16 for x in closed),backend='Assisted Gameplay assignment plus quoted treasury debit; native AI PURCHASE not proven.')

def focus_evidence(index,reference_resources,primary,owned_rows,reserved):
    # Retain the physical observation and prior plan even when the resource has
    # disappeared and therefore drops out of the current material-link census.
    physical=next((p for p in primary['plots']if p['index']==index),None)
    plans=[p for p in reserved if p['plot']==index]
    return dict(physical_observed=physical is not None,physical=physical,
                resource_presence_by_reference={name:(physical.get('resource')==name if physical is not None else None)for name in reference_resources},
                owned_material_rows=[r for r in owned_rows if r['plot']==index],
                first_logged_city_improvement_plan=first_logged_plans(plans),all_logged_reserved_plans=plans,
                cause_of_absence_inferred=False)

def endpoint_spillover(pasture,trial):
    a,b=[read(Path(r)/'final-native-private-snapshot.json')for r in(pasture,trial)]
    primary=[read(Path(r)/'game-01/turn-075.json')for r in(pasture,trial)]
    for root in(pasture,trial):
        boundary=read(Path(root)/'final-native-private-boundary.json')
        assert all(x['turn']==75 and not x['active']and x['remaining']==0 for x in(boundary['before'],boundary['after']))
    old={(c['player'],c['id']):c for c in primary[0]['cities']};new={(c['player'],c['id']):c for c in primary[1]['cities']};changes=[]
    for row in allocation_difference(a,b):
        if not row['changed_worked_plots']:continue
        key=(row['player'],row['city']);names={k for k in old[key]['yields'].keys()|new[key]['yields'].keys()if not k.startswith('YIELD_CSC_AI_')}
        delta={k:new[key]['yields'].get(k,0)-old[key]['yields'].get(k,0)for k in names}
        changes.append(dict(**row,derived_city_economic_delta=delta,worked_and_city_output_directions_correspond=channels_correspond(row['worked_plot_economic_delta'],delta)))
    return dict(physical_world_signature_equal=world_signature(primary[0])==world_signature(primary[1]),worker_allocation_changes=changes,physical_structure_equality_is_not_economic_inertness=True,raw_UI_turns=[a['turn'],b['turn']],isolated_zero_turn_signal_test=False)

def verify_pair(roots,turn):
    control,pasture,trial=roots;audits=[read(r/'independent-diagnostic-audit.json')for r in roots[:2]]
    assert all(x['verified']and x['endpoint']==75 and x['runtime_restored510']for x in audits)
    startup=read(trial/'independent-resource-improvement-startup-confirmation.json');assert startup['verified']and startup['strict_source16_equal_to_raw_control']and startup['exact_three_loaded_improvement_rows']
    proof=read(trial/'source-validation.json');assert not proof['runtime_harvest_rule']and not proof['measured_rule_legality']and proof['loads']==1 and proof['new_worlds']==0
    assert proof['source_sha256']==audits[0]['source_sha256']==audits[1]['source_sha256']
    initial=[read(r/'source16-initial.json')for r in roots]
    for value in initial[1:]:source_parity(initial[0],value,{})
    verify_source(initial[2]);current=sqlite3.connect((trial/'native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True);raw=sqlite3.connect((control/'native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True)
    try:loaded=verify_loaded(current,raw)
    finally:current.close();raw.close()
    pins=read(trial/'executed-source-pins.json');archives={sha(p)for p in(trial/'source-version').iterdir()if p.is_file()};assert set(pins.values())<=archives
    final=turn==75
    if final:
        audit=read(trial/'independent-diagnostic-audit.json');assert audit['verified']and audit['resource_improvement_forecast_diagnostic']and audit['runtime_restored510']and audit['endpoint']==75
        assert read(trial/'job-status.json')['status']=='complete'and read(trial/'supervisor.json')['exit_code']==0
        snap=verify_final_snapshot(read(trial/'final-native-private-snapshot.json'),read(trial/'game-01/turn-075.json'),read(trial/'final-native-private-boundary.json'))
        assert snap==read(trial/'final-resource-improvement-private-proof.json')
    else:
        assert all(sha(p)==value for p,value in pins.items()),'Live source pin drift'
        snap=None
    return dict(loaded=loaded,pins_archived=len(pins),all_final_audits_verified=final,final_private=snap,source_sha256=proof['source_sha256'])

def compare(roots,turn):
    assert turn in(25,50,75),'Declared closed checkpoint required'
    roots=tuple(map(Path,roots));proof=verify_pair(roots,turn);out={};materials={};counts={};closed={};physical_by_label={};plans_by_label={}
    for label,root in zip(LABELS,roots):
        # The exact saved checkpoint receipt must already exist, never a partial
        # outcome being published by the worker at the time of this read.
        assert(root/'exact-checkpoints'/f'turn-{turn:03d}.json').exists(),'Outcome checkpoint not yet closed/saved'
        primary=read(root/'game-01'/f'turn-{turn:03d}.json');point=read(root/'metric-points'/f'turn-{turn:03d}.json');care=read(root/'material-care'/f'turn-{turn:03d}.json')
        assert primary['turn']==point['turn']==care['turn']==turn and not care['errors']
        tree,cov=reconstruct_checkpoint(root,'AI_Behavior_Trees.csv',turn);reserved=reservations(tree,turn,primary['width']);reserved=[r for r in reserved if r['turn']>=16]
        physical_by_label[label]=primary;plans_by_label[label]=reserved
        rows=material_rows(point,care,reserved,primary);materials[label]=rows
        counts[label]=dict(point['counts'])
        states=collections.Counter(r['care_state']for r in rows)
        actionable_no_plan=[r for r in rows if r['care_state']=='develop'and r['no_logged_reserved_city_improvement_plan']]
        # A reservation under another tree (e.g. tech boost) is not omitted from
        # raw evidence or silently called a city-improvement job.
        out[label]=dict(root=str(root),counts=point['counts'],funding=funding(root,turn),closed_native_outcomes=checkpoint(root,turn),research=checkpoint_research(root,turn),owned_unique_material_plots=len(rows),material_states=dict(states),actionable_without_logged_city_improvement_plan=[dict(player=r['player'],plot=r['plot'],resource=r['resource'],care=r['care'],other_tree_reservations=[p for p in r['all_logged_reserved_plans']if p.get('tree')!='Build City Improvement'])for r in actionable_no_plan],native_work=work_report(root,turn))
        closed[label]=cov
    identifiers=sorted(set(SENTINELS)|{r['plot']for rows in materials.values()for r in rows if 'spec'in r['categories']})
    initial=read(roots[0]/'source16-initial.json');focus=[]
    for index in identifiers:
        resources={p['resource']for p in initial['world']['plots']if p['index']==index and p.get('resource')}
        resources.update(r['resource']for values in materials.values()for r in values if r['plot']==index)
        resources=sorted(resources)
        focus.append(dict(plot=index,reference_resources=resources,trajectories={label:focus_evidence(index,resources,physical_by_label[label],materials[label],plans_by_label[label])for label in LABELS}))
    return dict(through=turn,one_saved_world=True,new_worlds=0,full_independent_audit=turn==75,verification=proof,counts=counts,trajectories=out,owned_material_rows=materials,focus=focus,exact_closed_tree_logs=closed,endpoint_citizen_spillover=endpoint_spillover(roots[1],roots[2])if turn==75 else None,actual_Service_payments='UNOBSERVED',limits=['One source16 saved-world counterfactual with different downstream economies/intervention exposure; not independent samples or whole-mod causal gain.','Direct improvement forecast is broad/all-owner including humans; equal physical structure does not mean equal citizen allocation or ordinary city output.','Missing native/physical/care observations are UNOBSERVED, not zero or destruction.','No logged city-improvement reservation is bounded to captured logs; other trees/hidden commitments may exist.','Nearby Builders and charge counts do not prove idleness, task availability or reachability.','Care working and producer links are structural proxies; exact Service transactions unobserved.','Sparse physical checkpoints do not prove uninterrupted retention; work transitions/events/logs provide separate evidence.'])

def markdown(v):
    lines=['# Resource-compatible improvement forecast, turn'+str(v['through']),'','One exact saved-world counterfactual; '+('all final audits verified.'if v['full_independent_audit']else'closed intermediate evidence, final audit pending.'),'','| Metric | Raw | Pasture | Pasture + Camp + Plantation |','|---|---:|---:|---:|']
    for name in v['counts']['raw_control']:lines.append('| '+name+' | '+' | '.join(str(v['counts'][k][name])for k in LABELS)+' |')
    lines+=['','| Material work | Raw | Pasture | Three improvement types |','|---|---:|---:|---:|']
    for name in('working','develop','repair','locked_or_illegal','unsafe','inaccessible','UNOBSERVED'):
        lines.append('| '+name+' | '+' | '.join(str(v['trajectories'][k]['material_states'].get(name,0))for k in LABELS)+' |')
    lines+=['','See comparison.json for per-plot prerequisites/care/plans, native work and receipts.','','Limits:']+['- '+x for x in v['limits']]
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('control',type=Path);parser.add_argument('pasture',type=Path);parser.add_argument('trial',type=Path);parser.add_argument('--turn',type=int,required=True,choices=(25,50,75));parser.add_argument('--output',type=Path,required=True);a=parser.parse_args()
    v=compare((a.control,a.pasture,a.trial),a.turn);a.output.mkdir(parents=True,exist_ok=True);(a.output/'comparison.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8');(a.output/'comparison.md').write_text(markdown(v),encoding='utf-8');print(json.dumps(dict(through=a.turn,final_audit=v['full_independent_audit'],counts=v['counts'],material_states={k:x['material_states']for k,x in v['trajectories'].items()})))
