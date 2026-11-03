"""Offline source16..75 raw-control versus backlog/boost scheduling diagnostic."""
import argparse,json,hashlib
from pathlib import Path
from material_forecast_contract import source_parity
from material_forecast_variants import declared_database_delta
from material_forecast_comparison import case_state
from material_job_origin_intelligence import report as origin_report
from material_boost_log import report as boost_report,events_for_job
from material_boost_activity import report as activity_report

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def loss_union(audits):
    found={}
    for label,audit in zip(('control','boost_gate'),audits):
        for case in audit['loss_attribution']['cases']:
            resource=case.get('prior_resource')
            if resource is None:continue
            entry=found.setdefault((case['plot'],resource),dict(plot=case['plot'],resource=resource,losses={}))
            entry['losses'].setdefault(label,[]).append(case)
    return [found[key]for key in sorted(found)]

def observed_state(plot,resource,sites,reference,matching):
    value=case_state(plot,resource,sites,reference,matching);value['endpoint_plot_observed']=plot is not None
    if plot is None:value['resource_present_at_endpoint']=None
    return value

def compare(control,gate):
    control=Path(control);gate=Path(gate);audits=[read(p/'independent-diagnostic-audit.json')for p in(control,gate)]
    assert all(a['verified']and a['endpoint']==75 and a['arm']=='raw-resource'and a['runtime_restored510']for a in audits)
    assert audits[1]['branch']=='boost-gate-v3'and audits[1]['boost_gate_diagnostic']
    assert audits[1]['raw_control_audit_sha256']==sha(control/'independent-diagnostic-audit.json')
    assert audits[0]['source_sha256']==audits[1]['source_sha256']
    source_parity(read(control/'source16-initial.json'),read(gate/'source16-initial.json'),{})
    base=read(control.parent/'run-01/native-database-inventory.json');raw=read(control/'native-database-inventory.json');native=read(gate/'native-database-inventory.json')
    delta=declared_database_delta(base,native,treatment=True,boost_gate=True,raw_control=raw)
    roots=(control,gate);points=[read(p/'metric-points/turn-075.json')for p in roots];primary=[read(p/'game-01/turn-075.json')for p in roots]
    focused=[]
    for entry in loss_union(audits):
        index=entry['plot'];resource=entry['resource'];reference=[dict(plot=s['plot'],quarter=s['quarter'],player=s['player'])for s in points[0]['sites']if any(m['plot']==index and m['resource']==resource and m['category']=='base'for m in s['materials'])]
        states=[]
        for census,point in zip(primary,points):
            plot=next((p for p in census['plots']if p['index']==index),None)
            matching=[dict(plot=s['plot'],quarter=s['quarter'],player=s['player'])for s in point['sites']if any(m['plot']==index and m['resource']==resource and m['category']=='base'for m in s['materials'])]
            states.append(observed_state(plot,resource,point['sites'],reference,matching))
        focused.append(dict(**entry,control=states[0],boost_gate=states[1],reference_Quarter_scope='Observed control endpoint material links only; already removed resources cannot establish a missing historical Quarter link.'))
    origins=[origin_report(p,75)for p in roots];boosts=[boost_report(p,75)for p in roots];activity=[activity_report(p,75)for p in roots]
    for origin,boost in zip(origins,boosts):
        for case in origin['cases']:case['matching_boost_records_at_or_after_first_reservation']=events_for_job(case,boost['events'])
    return dict(verified_pair=True,source_sha256=audits[0]['source_sha256'],endpoint=75,new_worlds=0,independent_world_samples=1,intentional_counterfactual_replay='16..75 in each trajectory; same pre16 prefix inherited separately once, never summed',initial_world_units_treasury_production_private_and_city_output_equal=True,native_database_delta_from_original512=delta,counts={label:a['AI_counts']for label,a in zip(('control','boost_gate'),audits)},economic_effects={label:dict(funding=a['funding'],new_tiles=a['new_tile_acquisitions'],new_cost=a['new_gold_spent'],new_donations=a['new_donations'],foundations=a['foundations'])for label,a in zip(('control','boost_gate'),audits)},loss_summaries={label:a['loss_attribution']['summary']for label,a in zip(('control','boost_gate'),audits)},focus_cases=focused,job_origins=dict(zip(('control','boost_gate'),origins)),observed_boost_reservation_routes=dict(zip(('control','boost_gate'),activity)),boost_records=dict(zip(('control','boost_gate'),boosts)),repairs={label:a['repair_episodes']for label,a in zip(('control','boost_gate'),audits)},limits=['Temporary player-wide handler preference, not per-plot protection.','Lower or absent boost-origin jobs alone does not prove native boolean consumption or universal causality.','Helpful improvement-count boosts may also be delayed; native boost records are reported without invented initial state/counts.','Sparse endpoints cannot establish uninterrupted retention; absent census plots remain unobserved.','Private raw resource citizen effects remain in BOTH arms; neither arm is AI-only release tuning.','No actual Service payments or causal whole-mod gains inferred.'])

def markdown(value):
    lines=['# Backlog/boost scheduling diagnostic, matched source16..75','','Both arms have independent native75/normal-exit/original510 audits. These are counterfactual trajectories of one saved world.','','| Metric | Raw control | Temporary boost gate |','|---|---:|---:|']
    for key,left in value['counts']['control'].items():lines.append(f'| {key} | {left} | {value["counts"]["boost_gate"][key]} |')
    lines+=['','Loss classifications: `'+json.dumps(value['loss_summaries'])+'`.','','New acquisitions exclude the shared turn15 purchase25own. See JSON for receipts, separate funds/donations, foundations, matched repair episodes and individual loss outcomes.','','Job origins: `'+json.dumps({k:v['summary']for k,v in value['job_origins'].items()})+'`.','','Native boost events retain their original Progress label. Absence of a matching event16..75 does not supply the initial source16 boost state or prove a particular job failed to cause a boost.','','Limits:']+['- '+x for x in value['limits']]
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('control',type=Path);p.add_argument('gate',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();value=compare(a.control,a.gate);a.output.mkdir(parents=True,exist_ok=True);(a.output/'comparison.json').write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8');(a.output/'comparison.md').write_text(markdown(value),encoding='utf-8');print(json.dumps(dict(verified_pair=value['verified_pair'],counts=value['counts'],loss_summaries=value['loss_summaries'])))
