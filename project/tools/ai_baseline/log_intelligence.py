"""Offline AI-log intelligence from archived, byte-offset checkpoint segments.

No native imports or connections. Contract records repeated in different cities
are one contract, not multiple trained units. Tree records are evaluations, not
independent jobs. Accepted intervals are explicit, including same-world reloads.
"""
from __future__ import annotations
import argparse,collections,csv,gzip,json,re,statistics
from pathlib import Path

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def reconstruct(root:Path,name:str):
    segments=[]
    for manifest in (root/'diagnostics').glob('*/log-segments.json'):
        for row in read(manifest):
            archive=manifest.parent/(name+'.gz')
            if row['file']==name and row.get('bytes',0)>0 and archive.exists():
                segments.append((row['start'],row['end'],archive))
    data=bytearray();gaps=[];conflicts=[];seen=set()
    for start,end,path in sorted(segments,key=lambda x:(x[0],x[1],str(x[2]))):
        chunk=gzip.decompress(path.read_bytes())
        if len(chunk)!=end-start:raise ValueError(f'Segment size differs: {path}')
        key=(start,end,chunk)
        if key in seen:continue
        seen.add(key)
        if start>len(data):gaps.append([len(data),start]);data.extend(b'\n'*(start-len(data)))
        overlap=max(0,min(len(data),end)-start)
        if overlap and data[start:start+overlap]!=chunk[:overlap]:conflicts.append(str(path));continue
        data.extend(chunk[overlap:])
    return data.decode('utf-8',errors='replace'),dict(bytes=len(data),segments=len(segments),gaps=gaps,conflicting_segments=conflicts)

def records(text,first,last,players):
    for raw in text.splitlines():
        try:row=next(csv.reader([raw],skipinitialspace=True));turn=int(row[0]);player=int(row[1])
        except (ValueError,IndexError,csv.Error):continue
        if first<=turn<=last and player in players:yield turn,player,[x.strip()for x in row],raw

def summarize_contracts(rows):
    contracts={};selections=[]
    for turn,player,row,raw in rows:
        match=re.search(r'\bCONTRACT (\d+)',raw)
        if not match:continue
        item=next((x for x in row if re.fullmatch(r'(UNIT|BUILDING|DISTRICT|PROJECT)_[A-Z0-9_]+',x)),None)
        if item is None:continue
        contract=contracts.setdefault((player,int(match[1])),dict(player=player,id=int(match[1]),items=set(),cities=set(),events=[]))
        contract['items'].add(item);contract['cities'].add(row[2])
        status=next((x for x in row if x in ('SUBMITTED','ACCEPTED','IN PROGRESS','COMPLETED','CANCELLED','FAILED')),None)
        if status is None and len(row)>6 and row[5]==item:
            status='SELECTED';selections.append(dict(turn=turn,player=player,city=row[2],item=item,contract=int(match[1])))
        if status:contract['events'].append(dict(turn=turn,status=status,city=row[2],raw=raw))
    output=[]
    for c in contracts.values():
        c['items']=sorted(c['items']);c['cities']=sorted(c['cities']);c['events'].sort(key=lambda e:e['turn'])
        for field,status in [('submitted','SUBMITTED'),('selected','SELECTED'),('completed','COMPLETED')]:
            c[field]=min((e['turn']for e in c['events']if e['status']==status),default=None)
        # Terminal outcomes are allowed to coexist across production cities.
        c['cancelled_or_failed']=any(e['status']in ('CANCELLED','FAILED')for e in c['events'])
        c['submission_to_selection']=None if c['submitted']is None or c['selected']is None else c['selected']-c['submitted']
        c['submission_to_completion']=None if c['submitted']is None or c['completed']is None else c['completed']-c['submitted']
        output.append(c)
    return output,selections

def repair_episodes(events,builder_events,width):
    opened={};out=[]
    operations={(e['turn'],e['player'],e.get('y',-999)*width+e.get('x',-999))for e in builder_events if e.get('operation')==147469951}
    for e in events:
        key=e['player'],e['plot']
        if e['event']=='work_state'and e.get('state')=='repair':
            opened.setdefault(key,dict(player=key[0],plot=key[1],start=e['turn'],left_censored=e.get('previous')=='new'))
        elif e['event']=='work_state'and e.get('state')=='working'and key in opened:
            row=opened.pop(key);row.update(end=e['turn'],elapsed=e['turn']-row['start'],native_repair_matched=(e['turn'],*key)in operations,outcome='working');out.append(row)
        elif e['event']=='supply_lost'and key in opened:
            row=opened.pop(key);row.update(end=e['turn'],outcome='resource_lost');out.append(row)
    return out+[dict(v,outcome='pending_at_last_care_checkpoint')for v in opened.values()]

def analyze(intervals,players,current):
    names=['AI_CityBuild.csv','AI_Behavior_Trees.csv','AI_Operation.csv','AI_Operation_Eval.csv','AI_Research.csv','AI_GovtPolicies.csv','AI_Planning.csv','Game_RandomEvents.csv','City_BuildQueue.csv','UnitOperations.log']
    coverage=[];by_name=collections.defaultdict(list);disasters=[]
    for root,first,last in intervals:
        for name in names:
            text,info=reconstruct(root,name);coverage.append(dict(root=str(root),file=name,accepted_first=first,accepted_last=last,**info))
            by_name[name].extend(records(text,first,last,players))
            if name=='Game_RandomEvents.csv':
                for line in text.splitlines():
                    try:turn=int(line.split(',')[0])
                    except ValueError:continue
                    if first<=turn<=last and any(k in line for k in ('ERUPTION','FLOOD','STORM','DROUGHT')):disasters.append(line)
    contracts,selections=summarize_contracts(by_name['AI_CityBuild.csv'])
    categories={}
    for label,predicate in [('builders',lambda x:'UNIT_BUILDER'in x['items']),('csc_buildings',lambda x:any(i.startswith('BUILDING_CSC_')for i in x['items'])),('districts',lambda x:any(i.startswith('DISTRICT_')for i in x['items']))]:
        cohort=[x for x in contracts if predicate(x)];delays=[x['submission_to_selection']for x in cohort if x['submission_to_selection']is not None]
        categories[label]=dict(contracts=len(cohort),selected=sum(x['selected']is not None for x in cohort),completed=sum(x['completed']is not None for x in cohort),cancelled_or_failed_any_city=sum(x['cancelled_or_failed']for x in cohort),cross_city_submissions=sum(len([c for c in x['cities']if c!='PURCHASE'])>1 for x in cohort),median_observed_submission_to_selection=statistics.median(delays)if delays else None)
    building_items={}
    for item in sorted({i for c in contracts for i in c['items']if i.startswith('BUILDING_CSC_')}):
        cohort=[c for c in contracts if item in c['items']]
        building_items[item]=dict(contracts=len(cohort),selected=sum(c['selected']is not None for c in cohort),completed=sum(c['completed']is not None for c in cohort))
    nodes=collections.Counter();failure_samples={};builder_bidding=collections.Counter()
    for turn,p,row,raw in by_name['AI_Behavior_Trees.csv']:
        if len(row)<7 or row[3]!='Build City Improvement':continue
        nodes[(row[5],row[4])]+=1
        if row[4]=='FAILURE':failure_samples.setdefault(row[5],raw)
        if row[5]=='Build Unit':
            for key in ['Not Building','Accepted at','Building at','Rejected at']:
                if key in raw:builder_bidding[key]+=1
    care_paths=sorted((current/'material-care').glob('turn-*.json'));care=read(care_paths[-1]);builders=read(current/'failure-preserved-builders-current.json');primary=read(current/'failure-preserved-primary-current.json')
    points=[read(p)for p in sorted((current/'metric-points').glob('turn-*.json'))]
    return dict(scope='Observed accepted timeline; no causal baseline. Repeated tree records are not unique jobs. Cross-city cancellation is not necessarily final contract failure.',players=sorted(players),coverage=coverage,contracts=contracts,selections=selections,contract_summary=categories,building_contracts_by_item=building_items,builder_event_counts=dict(collections.Counter(e['event']for e in builders['events']if e.get('player')in players and any(first<=e['turn']<=last for _,first,last in intervals))),builder_tree_records=[dict(node=n,result=r,records=v)for(n,r),v in sorted(nodes.items())],builder_bid_records=dict(builder_bidding),tree_failure_examples=failure_samples,disaster_records=disasters,material_losses=[e for e in care['events']if e['event']=='supply_lost'],repair_episodes=repair_episodes(care['events'],builders['events'],primary['width']),care_last_turn=care['turn'],shortage_checkpoints=[dict(turn=read(p)['turn'],players={pid:v['shortage']for pid,v in read(p)['players'].items()if int(pid)in players})for p in care_paths],outcome_checkpoints=[dict(turn=p['turn'],counts=p['counts'])for p in points],other_log_rows={k:len(v)for k,v in by_name.items()})

def markdown(report):
    lines=['# Archived AI-log intelligence','','Accepted intervals are listed in the JSON coverage. Contracts are deduplicated by player and ID; tree records are repeated evaluations, not independent jobs.','','| Contract cohort | Contracts | Selected | Completed | Any-city cancel/fail | Multi-city | Median observed wait |','|---|---:|---:|---:|---:|---:|---:|']
    for label,row in report['contract_summary'].items():lines.append('| '+label+' | '+' | '.join(str(row[k])for k in ['contracts','selected','completed','cancelled_or_failed_any_city','cross_city_submissions','median_observed_submission_to_selection'])+' |')
    lines+=['','A cancellation in one production city may coexist with successful completion elsewhere. Missing starts/ends are censored.']
    lines+=['','Native observer Builder event counts are separate from production contracts: `'+json.dumps(report['builder_event_counts'],sort_keys=True)+'`. These event categories must not be summed as unique units.','','## CSC building contracts','','| Building | Contracts | Selected | Completed |','|---|---:|---:|---:|']
    for item,row in report['building_contracts_by_item'].items():lines.append('| '+item+' | '+' | '.join(str(row[k])for k in ['contracts','selected','completed'])+' |')
    lines+=['','## Native improvement-tree failure examples','']
    lines += ['- '+k+': `'+v+'`'for k,v in report['tree_failure_examples'].items()]
    lines+=['','## Material repair episodes','', '| Player | Plot | First repair observation | Working/lost | Elapsed | Outcome | Native repair matched |','|---|---:|---:|---:|---:|---|---|']
    for r in report['repair_episodes']:lines.append('| '+' | '.join(str(r.get(k,'UNOBSERVED'))for k in ['player','plot','start','end','elapsed','outcome','native_repair_matched'])+' |')
    lines+=['','Initial repair observations are left-censored; elapsed is observed time, not necessarily full pillage duration. Unsafe intervals are not subtracted.','', '## Limits','','No counterfactual AI game, internal district-site opportunity-cost score, or Service payment ledger is inferred. See JSON for log coverage/gaps and individual contract chronology.']
    return '\n'.join(lines)+'\n'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',type=Path,required=True);p.add_argument('--current',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    stopped=read(a.current/'job-status.json')['native_turn'];report=analyze([(a.parent,1,24),(a.current,25,stopped-1)],set(range(1,6)),a.current)
    a.output.mkdir(parents=True,exist_ok=True);(a.output/'ai-log-intelligence.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(a.output/'ai-log-intelligence.md').write_text(markdown(report),encoding='utf-8')
    print(json.dumps(dict(contract_summary=report['contract_summary'],care_last_turn=report['care_last_turn'],repair_episodes=len(report['repair_episodes']),coverage_warnings=[x for x in report['coverage']if x['gaps']or x['conflicting_segments']]),indent=2))

if __name__=='__main__':main()
