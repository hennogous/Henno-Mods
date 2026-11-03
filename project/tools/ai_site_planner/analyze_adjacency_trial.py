"""Read-only audit of the new adjacency-policy captures, including interruptions."""
import argparse,json,statistics
from pathlib import Path

def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def analyze(base):
 scans={};plans={};sources={}
 for directory in sorted(base.iterdir()):
  if not directory.is_dir():continue
  for path in (directory/'scans').glob('*.json'):
   data=read(path);turn=data['turn']
   if turn in scans:raise ValueError('Overlapping accepted scan turns require explicit reconciliation')
   scans[turn]=data;sources[turn]=str(path)
  for path in(directory/'plans').glob('*.json'):
   turn=int(path.stem.split('-')[-1]);plans[turn]=read(path)
 if not scans:raise ValueError('No completed scans')
 seen=set();foundations=[];promoted={};complete={};turns=sorted(scans)
 for i,turn in enumerate(turns):
  scan=scans[turn];prior=scans[turns[i-1]]if i else None
  prior_candidates={(r['player'],r['city'],r['quarter'],r['plot']):r for r in(prior or {}).get('candidates',[])}
  for r in plans.get(turns[i-1],{}).get('selected',[])if i else []:
   key=(r['player'],r['city'],r['quarter'],r['plot']);promoted.setdefault(key,[]).append(turns[i-1])
  for c in scan['cities']:
   for d in c['districts']:
    if d['type']not in('DISTRICT_CSC_BAKERS_QUARTER','DISTRICT_CSC_TAILORS_QUARTER'):continue
    key=(c['player'],c['city'],d['type'],d['plot'])
    if d['complete']and key not in complete:complete[key]=turn
    if key in seen:continue
    seen.add(key);candidate=prior_candidates.get(key)
    foundations.append(dict(player=c['player'],city=c['city'],cityName=c['name'],quarter=d['type'],plot=d['plot'],firstObserved=turn,completeAtFirstObservation=d['complete'],cityPresentInPreviousScan=any((x['player'],x['city'])==(c['player'],c['city'])for x in(prior or {}).get('cities',[])),previousScanTurn=prior['turn']if prior else None,previousAdjacency=candidate['total']if candidate else None,previousBreakdown=candidate['details']if candidate else None,everPromotedBefore=bool(promoted.get(key)),promotedTurns=promoted.get(key,[]).copy(),priorScanSource=sources[prior['turn']]if prior else None))
 for row in foundations:row['firstObservedComplete']=complete.get((row['player'],row['city'],row['quarter'],row['plot']))
 windows=[];results=[];timeline=[]
 for directory in base.iterdir():
  journal=directory/'controller-journal.ndjson'
  if journal.is_file():
   for line in journal.read_text().splitlines():
    event=json.loads(line)
    if event.get('event')=='command-begin':timeline.append(dict(run=directory.name,unix=event.get('started_unix'),operation=event.get('label'),context=event.get('state'),sequence=event.get('number'),evidence=str(journal)))
  path=directory/'native-windows.json'
  if path.is_file():windows+=read(path)
  result=directory/'result.json'
  if result.is_file():results.append(read(result))
 records=[(w,r)for w in windows for r in w['records']]
 winners=[dict(version=w['version'],policyScanTurn=w['version']-1,**r,promoted=any((e['player'],e['city'],e['district'],e['plot'])==(r['player'],r['city'],r['district'],r['plot'])for e in w['entries']))for w,r in records if r['k']=='best']
 durations=[s['elapsedSeconds']for s in scans.values()]
 return dict(acceptedScanTurns=turns,missingScanTurns=sorted(set(range(min(turns),max(turns)+1))-set(turns)),speed=sorted({s['speed']for s in scans.values()}),originalAI=scans[turns[0]]['originalAI'],foundations=foundations,promotedFoundations=sum(r['everPromotedBefore']for r in foundations),otherFoundations=sum(not r['everPromotedBefore']for r in foundations),knownBelow4Foundations=sum(r['previousAdjacency']is not None and r['previousAdjacency']<4 for r in foundations),completedQuarters=sum(r['firstObservedComplete']is not None for r in foundations),scanCPUSeconds=dict(median=statistics.median(durations),maximum=max(durations),validTimingEstablished=any(v>0 for v in durations),note='All-zero samples are below resolution or unavailable, not proof of zero cost'),geometryBuilds=sum(s['geometryBuilt']for s in scans.values()),cityObservations=sum(len(s['cities'])for s in scans.values()),evaluatedSitePairs=sum(s['sitesEvaluated']for s in scans.values()),nativeWindows=len(windows),nativeWrites=sum(w['stats']['changed']for w in windows),nativeErrors=sum(w['stats']['errors']for w in windows),nativeWinnerCalls=winners,operationTimeline=sorted(timeline,key=lambda e:e['unix']or 0),nativeWindowSummaries=[dict(version=w['version'],sourceScanTurn=w['version']-1 if w['version']>1 else None,entries=w['entries'],stats=w['stats'])for w in windows],results=results,causedChoiceChangeProven=False,economicBenefitProven=False,classification='Adjacency is the preceding completed scan, not an exact construction-tick re-evaluation; promoted means selected by this policy before first physical observation.')
def main():
 p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();result=analyze(a.base);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in('foundations','nativeWinnerCalls','results','operationTimeline','nativeWindowSummaries')}))
if __name__=='__main__':main()
