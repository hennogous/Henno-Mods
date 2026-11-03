"""Offline paired forecast results, distinguishing retained tiles from supply.

Requires both independently audited trajectories. No native client. A resource
remaining on the map is not success if its reference Quarter never exists, the
material is foreign/unimproved, or the producer is absent or pillaged.
"""
import argparse,json,time
from pathlib import Path
from material_decision_intelligence import report as decision_report
from material_care_audit import read,require

def case_state(plot,resource,sites,reference_quarters,matching_quarters=()):
    retained=plot is not None and plot.get('resource')==resource
    observed=[]
    original_keys={(x['plot'],x['quarter'])for x in reference_quarters}
    targets=list(reference_quarters)+[x for x in matching_quarters if (x['plot'],x['quarter'])not in original_keys]
    for original in targets:
        site=next((s for s in sites if s['plot']==original['plot']and s['quarter']==original['quarter']),None)
        if site is None:
            observed.append(dict(plot=original['plot'],quarter=original['quarter'],current_Quarter_in_AI_census=False,missing_scope='Absent or outside current major-AI census; destruction not inferred',material_owned=False,material_working=False,functioning_producer=False));continue
        material=next((m for m in site['materials']if m['plot']==plot['index']and m['category']=='base'and m['resource']==resource),None)if retained else None
        owned=bool(material and material['owner']==site['player']);working=bool(owned and material.get('improvement')and not material.get('pillaged',False))
        functioning=bool(working and site['complete']and not site['pillaged']and site['producer_built'])
        observed.append(dict(plot=site['plot'],quarter=site['quarter'],player=site['player'],current_Quarter_in_AI_census=True,complete=site['complete'],pillaged=site['pillaged'],producer_built=site['producer_built'],material_owned=owned,material_working=working,functioning_producer=functioning))
    return dict(resource_present_at_endpoint=retained,endpoint_owner=plot.get('owner')if plot else None,endpoint_improvement=plot.get('improvement')if plot else None,endpoint_pillaged=plot.get('pillaged')if plot else None,same_physical_reference_Quarters=[x for x in observed if (x['plot'],x['quarter'])in original_keys],alternative_matching_Quarters=[x for x in observed if (x['plot'],x['quarter'])not in original_keys],owned_material_for_reference_Quarter=any(x['material_owned']for x in observed if (x['plot'],x['quarter'])in original_keys),working_material_for_reference_Quarter=any(x['material_working']for x in observed if (x['plot'],x['quarter'])in original_keys),functioning_reference_producer=any(x['functioning_producer']for x in observed if (x['plot'],x['quarter'])in original_keys),working_material_for_any_matching_Quarter=any(x['material_working']for x in observed),any_functioning_matching_producer=any(x['functioning_producer']for x in observed),endpoint_only=True,uninterrupted_material_availability_proven=False)

def harvest_case_union(decisions):
    """Include harms in either arm; a retained reference target alone is insufficient."""
    found={}
    for arm,decision in zip(('reference','raw-resource'),decisions):
        for case in decision['cases']:
            key=(case['plot'],case['resource'])
            entry=found.setdefault(key,dict(plot=key[0],resource=key[1],cases={}))
            entry['cases'].setdefault(arm,[]).append(case)
    return [found[key]for key in sorted(found)]

def compare(reference,raw):
    reference=Path(reference);raw=Path(raw);S=reference.parent;C=S/'source016-control'
    audits=[read(p/'independent-diagnostic-audit.json')for p in(reference,raw)]
    require(all(a['verified']and a['endpoint']==75 and a['new_worlds']==0 for a in audits),'Both audited75 arms required')
    require([a['arm']for a in audits]==['reference','raw-resource'],'Wrong arm ordering')
    require(audits[0]['source_sha256']==audits[1]['source_sha256']==read(C/'control-verification.json')['source_sha256'],'Not matched source')
    require(audits[0]['native_database_delta']==[]and audits[1]['native_database_delta']==['Resource_YieldChanges'],'Unexpected treatment scope')
    roots=[reference,raw];primary=[read(p/'game-01/turn-075.json')for p in roots];points=[read(p/'metric-points/turn-075.json')for p in roots]
    decisions=[decision_report(p,75)for p in roots]
    source=read(C/'world.json');sourceplots={p['index']:p for p in source['plots']}
    neighbours={}
    for city in read(C/'production-and-quotes.json')['cities']:
        for tile in city['tiles']:
            old=neighbours.get(tile['index']);require(old is None or old==set(tile['neighbors']),'Conflicting source adjacency');neighbours[tile['index']]=set(tile['neighbors'])
    focus=[]
    for focus_case in harvest_case_union(decisions):
        index=focus_case['plot'];resource=focus_case['resource'];reference_cases=focus_case['cases'].get('reference',[])
        case=min(reference_cases,key=lambda x:x['harvest_turn'])if reference_cases else None
        base_types={q for city in read(C/'production-and-quotes.json')['cities']for tile in city['tiles']if tile['index']==index for q in tile['base_for']}
        fixed_scope=index in neighbours and index in sourceplots
        original=[dict(plot=s['plot'],quarter=s['quarter'],player=s['player'])for s in points[0]['sites']if (fixed_scope and s['plot']in neighbours[index]and s['quarter']in base_types)or any(m['plot']==index and m['category']=='base'and m['resource']==resource for m in s['materials'])]
        states=[]
        for census,point,decision in zip(primary,points,decisions):
            plot=next((p for p in census['plots']if p['index']==index),None)
            base_types={q for city in read(C/'production-and-quotes.json')['cities']for tile in city['tiles']if tile['index']==index for q in tile['base_for']}
            matching=[dict(plot=s['plot'],quarter=s['quarter'],player=s['player'])for s in point['sites']if (fixed_scope and s['plot']in neighbours[index]and s['quarter']in base_types)or any(m['plot']==index and m['category']=='base'and m['resource']==resource for m in s['materials'])]
            state=case_state(plot,resource,point['sites'],original,matching)
            state['confirmed_native_harvests']=[c['harvest_turn']for c in decision['cases']if c['plot']==index]
            states.append(state)
        focus.append(dict(plot=index,resource=resource,source16_owner=sourceplots[index]['owner']if index in sourceplots else None,source16_adjacency_scope_observed=fixed_scope,harvest_case_arms=sorted(focus_case['cases']),harvest_cases_by_arm=focus_case['cases'],reference_harvest_turn=case['harvest_turn']if case else None,reference_first_care_observation=case['first_recorded_care_observation']if case else None,reference_first_matching_reservation=case['first_observed_matching_reservation']if case else None,reference_Quarter_plots=original,reference=states[0],raw_resource=states[1],raw_retains_resource_but_no_reference_Quarter=bool(states[1]['resource_present_at_endpoint']and not any(x['current_Quarter_in_AI_census']for x in states[1]['same_physical_reference_Quarters'])),raw_has_valid_functioning_alternative=bool(states[1]['any_functioning_matching_producer']and not states[1]['functioning_reference_producer'])))
    initialcities={(c['x'],c['y'])for c in source['cities']}
    settlements=[]
    for census in primary:
        cities={(c['player'],c['id'],c['name'],c['x'],c['y'])for c in census['cities']if c['player']in range(1,6)}
        settlements.append([dict(player=p,city=i,name=n,x=x,y=y)for p,i,n,x,y in sorted(cities)if (x,y)not in initialcities])
    return dict(verified_pair=True,endpoint=75,source_sha256=audits[0]['source_sha256'],new_worlds=0,diagnostic_trajectories=2,independent_world_samples=1,intentional_raw_replay='16..75 in each trajectory; pre16 prefix inherited separately once, never summed',focus_cases=focus,focus_selection='Union of confirmed native harvest cases in either trajectory; not restricted to reference losses',counts={a['arm']:a['AI_counts']for a in audits},new_acquisitions={a['arm']:dict(tiles=a['new_tile_acquisitions'],cost=a['new_gold_spent'],donations=a['new_donations'],own_gold=a['new_gold_spent']-a['new_donations'])for a in audits},endpoint_AI_city_locations_absent_from_source_major_census=dict(zip(('reference','raw-resource'),settlements)),city_location_scope='Spatial endpoint difference, not proven founding events; captures of cities outside the initial major-player census remain possible.',loss_summaries={a['arm']:a['loss_attribution']['summary']for a in audits},decision_reports=dict(zip(('reference','raw-resource'),decisions)),whole_mod_causal_effect_established=False,universal_preservation_proven=False,interpretation_limits=['Raw resource valuation also affects unowned plots and future settlement/ownership decisions.','A positive result cannot distinguish resource-forecast representation from earlier and broader signal timing by itself.','Material at endpoint alone is not a functioning supply chain; same physical reference Quarter, ownership, improvement and producer gates are reported separately.','No exact Service payments or uninterrupted retention are inferred.','One matched saved world is not multiple independent world samples.'],time=time.time())

def markdown(v):
    lines=['# Raw-resource forecast diagnostic — matched source16..75','','Both trajectories must have independent endpoint75 audits and original510/preferences restoration. This is one saved world with intentional counterfactual replays, not an untreated-AI baseline.','','Focus includes confirmed harvests in either trajectory, including new treatment losses. Missing source adjacency is disclosed; observed endpoint material links remain valid evidence.','','| Target | Reference harvest | Raw harvest | Reference resource present75 | Raw resource present75 | Raw working material for same Quarter | Raw same-reference producer | Raw any matching producer |','|---|---:|---:|---|---|---|---|---|']
    for c in v['focus_cases']:lines.append('| '+str(c['plot'])+' '+c['resource']+' | '+str(c['reference_harvest_turn'])+' | '+str([x['harvest_turn']for x in c['harvest_cases_by_arm'].get('raw-resource',[])])+' | '+' | '.join(str(x)for x in(c['reference']['resource_present_at_endpoint'],c['raw_resource']['resource_present_at_endpoint'],c['raw_resource']['working_material_for_reference_Quarter'],c['raw_resource']['functioning_reference_producer'],c['raw_resource']['any_functioning_matching_producer']))+' |')
    lines+=['','## Endpoint counts','','| Metric | Reference v2 | Raw resource |','|---|---:|---:|']
    for key,n in v['counts']['reference'].items():lines.append('| '+key+' | '+str(n)+' | '+str(v['counts']['raw-resource'][key])+' |')
    lines+=['','New acquisition costs exclude the shared turn15 inherited purchase: `'+json.dumps(v['new_acquisitions'])+'`.','','## Limits','']+['- '+x for x in v['interpretation_limits']]
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('reference',type=Path);p.add_argument('raw',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();v=compare(a.reference,a.raw);a.output.mkdir(parents=True,exist_ok=True);(a.output/'comparison.json').write_text(json.dumps(v,indent=2),encoding='utf-8');(a.output/'comparison.md').write_text(markdown(v),encoding='utf-8');print(json.dumps({k:v[k]for k in('verified_pair','focus_cases','counts')}))
