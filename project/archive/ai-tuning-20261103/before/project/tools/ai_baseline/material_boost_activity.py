from material_checkpoint_logs import reconstruct_checkpoint
"""Offline observed boost reservation routes, including non-destructive work."""
import json,sqlite3
from pathlib import Path
from log_intelligence import reconstruct,records
from material_decision_intelligence import reservations
from material_job_origin_intelligence import origin,strategy_at

def routes(reserved,boosts,care):
    grouped={}
    for row in reserved:
        if row['tree']!='Build City Improvement'or not row.get('improvement'):continue
        value=origin(row['system'],boosts)
        if value['kind']!='boost':continue
        key=(row['player'],row['system'],row['plot'],row['improvement'])
        grouped.setdefault(key,[]).append((row,value))
    out=[]
    for key,values in sorted(grouped.items()):
        values.sort(key=lambda pair:pair[0]['turn']);first,value=values[0]
        observations=[e for e in care['events']if e.get('player')==first['player']and e.get('plot')==first['plot']and e['turn']<=first['turn']and e.get('event')in('work_state','supply_lost')]
        last=max(enumerate(observations),key=lambda x:(x[1]['turn'],x[0]))[1]if observations else None
        out.append(dict(player=key[0],system=key[1],plot=key[2],improvement=key[3],first_observed_reservation=first['turn'],last_observed_reservation=values[-1][0]['turn'],reservation_log_records=len(values),first_reservation=first,origin=value,gated_improvement_count_handler=any(b.get('BoostClass')=='BOOST_TRIGGER_HAVE_X_IMPROVEMENTS'for b in value['loaded_boost_rows']),care_strategy_at_first_observation=strategy_at(care['strategy']['transitions'],first['player'],first['turn']),last_care_record_at_or_before_first_reservation=last,persistent_job_identity_proven=False))
    return out

def native_strategy_events(text,through):
    return [dict(turn=t,player=p,strategy=row[2],status=row[3],raw=raw)for t,p,row,raw in records(text,16,through,set(range(1,6)))if len(row)>=4 and row[2]=='STRATEGY_CSC_AI_MATERIAL_BACKLOG']

def native_strategy_at(events,player,turn):
    prior=[e for e in events if e['player']==player and e['turn']<=turn]
    if not prior:return dict(observed=False,following=None,last_event=None,within_turn_ordering_proven=False)
    last=max(enumerate(prior),key=lambda x:(x[1]['turn'],x[0]))[1]
    return dict(observed=True,following=True if last['status']=='Following'else False if last['status']=='Stopped'else None,last_event=last,within_turn_ordering_proven=False)

def report(root,through):
    root=Path(root);care=json.loads((root/'material-care'/f'turn-{through:03d}.json').read_text(encoding='utf-8-sig'));text,coverage=reconstruct_checkpoint(root,'AI_Behavior_Trees.csv',through)
    assert not coverage['gaps']and not coverage['conflicting_segments']
    width=json.loads((root/'game-01'/f'turn-{through:03d}.json').read_text(encoding='utf-8-sig'))['width']
    db=sqlite3.connect((root/'native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
    try:boosts=[dict(x)for x in db.execute('SELECT * FROM Boosts')]
    finally:db.close()
    values=routes(reservations(text,through,width),boosts,care)
    native_text,native_coverage=reconstruct_checkpoint(root,'AI_Victories.csv',through);assert not native_coverage['gaps']and not native_coverage['conflicting_segments'];native_events=native_strategy_events(native_text,through)
    for value in values:value['native_strategy_at_first_observation']=native_strategy_at(native_events,value['player'],value['first_observed_reservation'])
    return dict(through=through,first_observed_turn=16,routes=values,native_strategy_events=native_events,native_strategy_log_coverage=native_coverage,summary=dict(improvement_count_routes_first_observed_while_native_following=sum(v['gated_improvement_count_handler']and v['native_strategy_at_first_observation']['following']is True for v in values),observed_routes=len(values),improvement_count_routes=sum(v['gated_improvement_count_handler']for v in values),improvement_count_routes_first_observed_with_active_care=sum(v['gated_improvement_count_handler']and v['care_strategy_at_first_observation']['active']is True for v in values),marked_material_routes_first_observed_with_active_care=sum(v['gated_improvement_count_handler']and v['care_strategy_at_first_observation']['active']is True and v['last_care_record_at_or_before_first_reservation']is not None for v in values)),scope='Distinct player/system/plot/improvement reservation routes, not independent jobs; first observation may follow an earlier hidden queue commitment.',boolean_preference_consumption_proven=False,coverage=coverage)
