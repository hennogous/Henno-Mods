"""Offline evidence for guidance timing and pre-harvest improvement removal.

Care observation is not proof of decision-level influence. A same-plot Farm
reservation does not establish when an internal job was first queued, and a
request in UnitOperations alone does not prove an operation took effect.
"""
import argparse,json,re
from pathlib import Path
from log_intelligence import reconstruct,records
from material_loss_intelligence import report as loss_report,unit_operations,clear_targets,native_hash

def reservations(text,through,width):
    intent={};out=[]
    for turn,pid,row,raw in records(text,1,through,set(range(1,6))):
        if len(row)<7:continue
        context=(turn,pid,row[2],row[3])
        if row[5]=='Decode Trigger':
            match=re.search(r'Improve: (IMPROVEMENT_[A-Z0-9_]+); Value: ([0-9.]+)',raw)
            intent[context]=dict(improvement=match[1],value=float(match[2]),intent_raw=raw)if match else{}
        if row[5]!='Reserve Plot'or row[4]!='SUCCESS':continue
        match=re.search(r'Reserving plot (-?\d+) (-?\d+)',raw)
        if not match:continue
        x,y=map(int,match.groups())
        if x<0 or y<0:continue
        out.append(dict(turn=turn,player=pid,system=row[2],tree=row[3],plot=y*width+x,raw=raw,**intent.get(context,{})))
    return out

def preparation_operations(case,events,ops,targets,width,window=5):
    out=[]
    known=[e['record']for e in case['evidence']if e['kind']=='native_operation_started']
    units={e['unit']for e in known};names=('UNITOPERATION_REMOVE_IMPROVEMENT','UNITOPERATION_REMOVE_FEATURE')
    for event in events:
        if event.get('event')!='builder_operation_started'or event.get('unit')not in units or event['player']!=case['player']or not(case['turn']-window<=event['turn']<case['turn']):continue
        name=next((n for n in names if native_hash(n)==event.get('operation')),None)
        if name is None:continue
        exact=event.get('x',-1)>=0 and event.get('y',-1)>=0 and event['y']*width+event['x']==case['plot']
        matched=[t for t in targets if(t['turn'],t['player'],t['unit'])==(event['turn'],event['player'],event['unit'])]
        if not exact and {t['plot']for t in matched}!={case['plot']}:continue
        log=[x for x in ops if(x['turn'],x['player'],x['unit'])==(event['turn'],event['player'],event['unit'])and x['operation']==name]
        if not log:continue
        out.append(dict(name=name,turn=event['turn'],native_start=event,unit_operation_log=log,target_proof='native event coordinates'if exact else'unique tree target',same_unit_as_harvest=True))
    return out

def report(root,through,*,terminal=None):
    root=Path(root);read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
    losses=loss_report(root,through,terminal=terminal)
    care=read(Path(terminal)/'care.json'if terminal else root/'material-care'/f'turn-{through:03d}.json')
    if terminal:builders=read(Path(terminal)/'builders.json')
    else:builders=max((read(p)for p in(root/'builders').glob('turn-*.json')if read(p)['turn']<=through),key=lambda x:x['turn'])
    tree,tcov=reconstruct(root,'AI_Behavior_Trees.csv');optext,ocov=reconstruct(root,'UnitOperations.log')
    assert not tcov['gaps']and not tcov['conflicting_segments']and not ocov['gaps']and not ocov['conflicting_segments']
    reserved=reservations(tree,through,losses['width']);targets=clear_targets(tree,1,through,set(range(1,6)),losses['width']);ops=unit_operations(optext,1,through,set(range(1,6)))
    snapshots=[read(p)for p in(root/'game-01').glob('turn-*.json')if read(p)['turn']<=through]
    cases=[]
    for case in losses['cases']:
        if case['classification']!='native_harvest_confirmed':continue
        final=[e['record']for e in case['evidence']if e['kind']=='exact_tree_clear_target']
        systems={x['system']for x in final};improvements={x['planned_improvement']for x in final if'planned_improvement'in x}
        r=[x for x in reserved if x['player']==case['player']and x['plot']==case['plot']and x['turn']<=case['turn']and x['system']in systems and x.get('improvement')in improvements]
        observed=[e for e in care['events']if e.get('event')=='work_state'and e['player']==case['player']and e.get('plot')==case['plot']and e['turn']<=case['turn']]
        first=min((x['turn']for x in observed),default=None);develop=min((x['turn']for x in observed if x['state']=='develop'),default=None);reservation=min((x['turn']for x in r),default=None)
        prior=[]
        for snapshot in snapshots:
            if snapshot['turn']>=case['turn']:continue
            plot=next((x for x in snapshot['plots']if x['index']==case['plot']),None)
            if plot:prior.append(dict(turn=snapshot['turn'],plot=plot))
        prior.sort(key=lambda x:x['turn'])
        prep=preparation_operations(case,builders['events'],ops,targets,losses['width'])
        cases.append(dict(player=case['player'],plot=case['plot'],resource=case.get('prior_resource'),harvest_turn=case['turn'],planned_improvements=sorted(improvements),first_recorded_care_observation=first,first_recorded_develop_state=develop,first_observed_matching_reservation=reservation,care_to_reservation_turns=reservation-first if reservation is not None and first is not None else None,care_precedes_observed_reservation=first<reservation if reservation is not None and first is not None else None,care_events=observed,first_matching_reservation=next((x for x in r if x['turn']==reservation),None),preparation_operations=prep,last_pre_harvest_census=prior[-1]if prior else None,decision_level_causality=False))
    return dict(root=str(root),through=through,cases=cases,confirmed_harvest_cases=len(cases),same_unit_native_preparation_cases=sum(bool(x['preparation_operations'])for x in cases),scope='Actual care observations, same-player/plot/system improvement reservations and native starts plus independent operation log; not hidden job-queue creation time or a counterfactual choice.',limits=['Care observation precedes planning only to the extent that planning is logged; absence of an earlier logged reservation does not prove absence of an earlier queued job.','No private-yield value at the decision instant is inferred from care-state logs.','Operation starts plus removal state evidence are stronger than queued requests alone.','Sparse censuses do not establish uninterrupted improvement retention.'])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('--through',type=int,required=True);p.add_argument('--terminal',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();v=report(a.root,a.through,terminal=a.terminal);a.output.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps({k:v[k]for k in('confirmed_harvest_cases','same_unit_native_preparation_cases')}));print(json.dumps([{k:x[k]for k in('plot','harvest_turn','first_recorded_care_observation','first_observed_matching_reservation','care_to_reservation_turns')}for x in v['cases']]))
