"""Offline material-loss attribution from independent native log streams.

Never opens FireTuner. Handles last-charge operations whose observed unit has
already moved to the invalid (-9999,-9999) coordinates. A queued operation alone
is not proof of a successful harvest, and an ownership loss is not destruction.
"""
import argparse,csv,json,re,zlib
from pathlib import Path
from log_intelligence import reconstruct,records

def native_hash(name):
    n=(~zlib.crc32(name.encode('ascii')))&0xffffffff
    return n if n<2**31 else n-2**32
HARVEST=native_hash('UNITOPERATION_HARVEST_RESOURCE')

def unit_operations(text,first,last,players):
    out=[]
    for raw in text.splitlines():
        try:
            row=next(csv.reader([raw],skipinitialspace=True));turn=int(row[0]);pid=int(row[2])
        except (ValueError,IndexError,csv.Error):continue
        if len(row)<5 or not(first<=turn<=last and pid in players):continue
        unit=re.fullmatch(r'(UNIT_[A-Z0-9_]+)\s+\((\d+)\)',row[3].strip())
        operation=re.fullmatch(r'(UNITOPERATION_[A-Z0-9_]+)\s+\((-?\d+)\)',row[4].strip())
        if unit and operation:out.append(dict(turn=turn,player=pid,mode=row[1].strip(),unit_type=unit[1],unit=int(unit[2]),operation=operation[1],native_enum=int(operation[2]),raw=raw))
    return out

def clear_targets(text,first,last,players,width):
    contexts={};intent={};out=[]
    for turn,pid,row,raw in records(text,first,last,players):
        if len(row)<7:continue
        context=(turn,pid,row[2],row[3]);node,result=row[5],row[4]
        if node=='Decode Trigger':
            match=re.search(r'Improve: (IMPROVEMENT_[A-Z0-9_]+); Value: ([0-9.]+)',raw)
            intent[context]=dict(planned_improvement=match[1],job_value=float(match[2]),intent_raw=raw)if match else {}
        if node=='Reserve Plot':
            match=re.search(r'Reserving plot (-?\d+) (-?\d+)',raw)
            if match:
                x,y=map(int,match.groups());contexts[context]=dict(x=x,y=y,plot=y*width+x,raw=raw) if result in ('SUCCESS','READY','RUNNING') and x>=0 and y>=0 else None
        if node=='Clear Plot'and result=='SUCCESS':
            match=re.search(r'Clearing with (\d+)',raw);target=contexts.get(context)
            if match and int(match[1])>0 and target:out.append(dict(turn=turn,player=pid,unit=int(match[1]),tree=row[3],system=row[2],**target,**intent.get(context,{}),clear_raw=raw))
    return out

def attribute(loss,events,operations,targets,width):
    case=dict(loss);case['classification']='unresolved';case['evidence']=[]
    if loss['resource']>=0:
        case['classification']='ownership_link_lost'if loss['owner']!=loss['player']else'link_lost_resource_still_present'
        return case
    for e in events:
        if e.get('operation')!=HARVEST or(e['player'],e['turn'])!=(loss['player'],loss['turn']):continue
        exact=e.get('x',-1)>=0 and e.get('y',-1)>=0 and e['y']*width+e['x']==loss['plot']
        matches=[t for t in targets if(t['turn'],t['player'],t['unit'])==(e['turn'],e['player'],e['unit'])]
        # Two different target plots for the same unit/turn are ambiguous. Never
        # assign the last target retrospectively to every operation on that turn.
        plots={t['plot']for t in matches}
        if exact or plots=={loss['plot']}:
            case['classification']='native_harvest_confirmed';case['evidence'].append(dict(kind='native_operation_started',record=e))
            case['evidence']+= [dict(kind='exact_tree_clear_target',record=t)for t in matches if t['plot']==loss['plot']]
            case['evidence']+= [dict(kind='unit_operation_log',record=o)for o in operations if(o['turn'],o['player'],o['unit'])==(e['turn'],e['player'],e['unit'])and o['operation']=='UNITOPERATION_HARVEST_RESOURCE']
            case['position_recovered_from_tree']=not exact;return case
    if loss.get('district',-1)>=0:
        case['classification']='resource_removed_with_district_at_loss'
        case['limit']='Native district occupancy observed at removal; no permanent building or harvest action inferred.'
    return case

def report(root,through):
    read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));root=Path(root)
    care=read(root/'material-care'/f'turn-{through:03d}.json');primary=read(root/'game-01'/f'turn-{through:03d}.json')
    builder_file=max((p for p in(root/'builders').glob('turn-*.json')if read(p)['turn']<=through),key=lambda p:read(p)['turn']);builders=read(builder_file)
    unit_text,ucov=reconstruct(root,'UnitOperations.log');tree_text,tcov=reconstruct(root,'AI_Behavior_Trees.csv')
    for cov in(ucov,tcov):assert not cov['gaps']and not cov['conflicting_segments'],'Incomplete/conflicting log stream; attribution requires review'
    players=set(range(1,6));ops=unit_operations(unit_text,1,through,players);targets=clear_targets(tree_text,1,through,players,primary['width'])
    cases=[attribute(e,builders['events'],ops,targets,primary['width'])for e in care['events']if e['event']=='supply_lost'and e['turn']<=through and e['player']in players]
    snapshots=[read(p)for p in(root/'game-01').glob('turn-*.json')if read(p)['turn']<=through]
    for case in cases:
        prior=sorted((p for p in snapshots if p['turn']<case['turn']),key=lambda p:p['turn'],reverse=True)
        for p in prior:
            plot=next((x for x in p['plots']if x['index']==case['plot']),None)
            if plot and plot.get('resource'):
                case['prior_resource']=plot['resource'];case['prior_resource_census_turn']=p['turn'];break
    from collections import Counter
    return dict(root=str(root),through=through,partial=True,accepted_timeline='fresh root only',width=primary['width'],builder_export_turn=builders['turn'],coverage={'UnitOperations.log':ucov,'AI_Behavior_Trees.csv':tcov},unit_operation_rows=len(ops),clear_target_records=len(targets),summary=dict(Counter(c['classification']for c in cases)),cases=cases,decision_effectiveness_proven=False,attribution_limits='Exact native starts plus unique tree targets may recover post-consumption coordinates; queued requests alone never prove harvest. District occupancy is not proof of permanent construction.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('--through',type=int,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=report(a.root,a.through);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out['summary']))
