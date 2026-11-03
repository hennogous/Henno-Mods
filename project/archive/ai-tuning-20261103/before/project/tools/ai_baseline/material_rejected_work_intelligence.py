"""Offline rejected Builder work, requiring closed logs and conservative target links."""
import argparse,collections,json,re,sys
from pathlib import Path
from material_checkpoint_logs import reconstruct_checkpoint
from material_loss_intelligence import native_hash,unit_operations
from log_intelligence import records

WORK_OPERATIONS={'UNITOPERATION_HARVEST_RESOURCE','UNITOPERATION_BUILD_IMPROVEMENT','UNITOPERATION_REMOVE_IMPROVEMENT','UNITOPERATION_REMOVE_FEATURE','UNITOPERATION_REPAIR'}

def tree_work_links(text,first,last,width):
    targets={};intent={};links=[]
    for turn,pid,row,raw in records(text,first,last,set(range(1,6))):
        if len(row)<7:continue
        key=(turn,pid,row[2],row[3]);result,node=row[4],row[5]
        if node=='Decode Trigger':
            match=re.search(r'Improve: (IMPROVEMENT_[A-Z0-9_]+); Value: ([0-9.]+)',raw)
            intent[key]=dict(improvement=match[1],job_value=float(match[2]),raw=raw) if match else None
        if node=='Reserve Plot':
            match=re.search(r'Reserving plot (-?\d+) (-?\d+)',raw)
            targets[key]=dict(x=int(match[1]),y=int(match[2]),plot=int(match[2])*width+int(match[1]),raw=raw) if match and result in('SUCCESS','READY','RUNNING') and int(match[1])>=0 and int(match[2])>=0 else None
        if node!='Clear Plot' or targets.get(key) is None:continue
        match=re.search(r'Clearing with (\d+)',raw)
        if not match or int(match[1])==0:continue
        links.append(dict(turn=turn,player=pid,unit=int(match[1]),system=row[2],tree=row[3],target=targets[key],intent=intent.get(key),clear_node_result=result,clear_raw=raw))
    return links

def rejected_routes(operations,links,native_events):
    grouped={}
    for row in operations:
        if row['unit_type']!='UNIT_BUILDER' or row['mode']!="Can't Start" or row['operation'] not in WORK_OPERATIONS:continue
        matching=[l for l in links if(l['turn'],l['player'],l['unit'])==(row['turn'],row['player'],row['unit'])]
        plots={l['target']['plot'] for l in matching}
        plot=next(iter(plots)) if len(plots)==1 else None
        key=(row['player'],row['unit'],plot,row['operation'])
        g=grouped.setdefault(key,dict(player=row['player'],unit=row['unit'],plot=plot,operation=row['operation'],rejection_records=[],associated_tree_links=[],ambiguous_target_observations=[],native_start_events=[]))
        g['rejection_records'].append(row)
        for link in matching:
            if link not in g['associated_tree_links']:g['associated_tree_links'].append(link)
        if len(plots)!=1:g['ambiguous_target_observations'].append(dict(turn=row['turn'],candidate_plots=sorted(plots)))
        for event in native_events:
            if (event.get('player'),event.get('unit'),event.get('turn'),event.get('operation'))==(row['player'],row['unit'],row['turn'],native_hash(row['operation'])) and event not in g['native_start_events']:g['native_start_events'].append(event)
    out=[]
    for key,g in grouped.items():
        turns=sorted({r['turn'] for r in g['rejection_records']});g.update(first_observed_turn=min(turns),last_observed_turn=max(turns),observed_rejection_turns=turns,rejection_log_records=len(g['rejection_records']),unique_rejection_turns=len(turns),associated_tree_improvements=sorted({l['intent']['improvement'] for l in g['associated_tree_links'] if l['intent']}),no_matching_native_start_observed=not g['native_start_events'],request_parameters_logged=False,exact_build_improvement_parameter_proven=False,persistent_job_identity_proven=False)
        out.append(g)
    return sorted(out,key=lambda g:(g['player'],g['unit'],-1 if g['plot'] is None else g['plot'],g['operation']))

def development_episodes(care_events,native_events,plots,width):
    episodes=[]
    for event in care_events:
        if event.get('event')!='work_state' or event.get('state')!='working' or event.get('previous')!='develop' or event.get('player') not in range(1,6):continue
        candidates=[e for e in native_events if(e.get('player'),e.get('turn'),e.get('operation'))==(event['player'],event['turn'],native_hash('UNITOPERATION_BUILD_IMPROVEMENT'))]
        exact=[e for e in candidates if e.get('x',-1)>=0 and e.get('y',-1)>=0 and e['y']*width+e['x']==event['plot']]
        physical=next((p for p in plots if p['index']==event['plot']),None)
        episodes.append(dict(player=event['player'],plot=event['plot'],turn=event['turn'],resource_enum=event['resource'],work_transition=event,exact_plot_native_build_starts=exact,same_player_turn_native_build_candidates=candidates,native_build_at_exact_plot_confirmed=bool(exact),unit_attribution_proven=len(exact)==1,endpoint_plot_observation=physical,endpoint_census_does_not_prove_uninterrupted_retention=True))
    return episodes

def report(root,through):
    root=Path(root);read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
    primary=read(root/'game-01'/f'turn-{through:03d}.json');builders=read(root/'builders'/f'turn-{through:03d}.json');care=read(root/'material-care'/f'turn-{through:03d}.json');assert primary['turn']==builders['turn']==care['turn']==through
    tree,tcov=reconstruct_checkpoint(root,'AI_Behavior_Trees.csv',through);ops,ocov=reconstruct_checkpoint(root,'UnitOperations.log',through)
    links=tree_work_links(tree,16,through,primary['width']);routes=rejected_routes(unit_operations(ops,16,through,set(range(1,6))),links,builders['events'])
    for route in routes:
        unit=next((u for p in builders['players'] if p['player']==route['player'] for u in p['builders'] if u['unit']==route['unit']),None)
        route['endpoint_Builder_observation']=unit;route['endpoint_Builder_on_associated_plot']=(unit['y']*primary['width']+unit['x']==route['plot']) if unit and route['plot'] is not None else None
        route['endpoint_plot_observation']=next((p for p in primary['plots'] if p['index']==route['plot']),None) if route['plot'] is not None else None
        route['endpoint_care_work']=next((p for p in care['players'].get(str(route['player']),{}).get('plots',[]) if p['plot']==route['plot']),None)
        route['material_care_events']=[e for e in care['events'] if e.get('player')==route['player'] and e.get('plot')==route['plot'] and 16<=e['turn']<=through] if route['plot'] is not None else []
    return dict(root=str(root),through=through,first_observed_turn=16,routes=routes,development_episodes=development_episodes(care['events'],builders['events'],primary['plots'],primary['width']),summary=dict(rejected_work_log_records=sum(r['rejection_log_records'] for r in routes),observed_routes=len(routes),uniquely_targeted_routes=sum(r['plot'] is not None for r in routes),multi_turn_rejection_routes=sum(r['unique_rejection_turns']>1 for r in routes),multi_turn_rejection_routes_without_matching_native_start=sum(r['unique_rejection_turns']>1 and r['no_matching_native_start_observed'] for r in routes),endpoint_Builders_on_repeated_rejected_target=len({(r['player'],r['unit']) for r in routes if r['unique_rejection_turns']>1 and r['endpoint_Builder_on_associated_plot'] is True})),coverage={'AI_Behavior_Trees.csv':tcov,'UnitOperations.log':ocov},limits=['Behavior-tree SUCCESS is node bookkeeping, not proof that a native operation started or changed a plot.','Rejected-operation log records need not be unique requests; retries may appear without a new Adding record.','Only a unique same-player/unit/turn reserved tree target is associated; conflicting or absent target plots remain unknown.','UnitOperations does not expose BuildImprovement parameters here; associated Farm/Pasture tree intent is not exact native request payload proof.','A repeated rejected route plus endpoint Builder position does not prove uninterrupted idling, hidden job identity or universal cause.','Matching native starts are reported even alongside rejections; no start observed is bounded to the captured event prefix.'])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('--through',type=int,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();v=report(a.root,a.through);a.output.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8');print(json.dumps(v['summary']))
