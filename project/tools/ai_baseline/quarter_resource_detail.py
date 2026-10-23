"""Offline per-player CSC Quarter detail and last-observed resource replacement audit."""
import argparse,bisect,json,sqlite3,shutil
from collections import Counter,defaultdict
from pathlib import Path
from analyze import STAGES,analyze

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def active(c):return {b['type'] for b in c['buildings'] if not b['pillaged']}
def visible(res,player,defs):
 d=defs.get(res,{})
 return (not d.get('PrereqTech') or d['PrereqTech'] in player['techs']) and (not d.get('PrereqCivic') or d['PrereqCivic'] in player['civics'])
def sums(rows,fields):return {k:sum(r.get(k,0) for r in rows) for k in fields}

def analyze_detail(folder,turn,defs):
 s=read(folder/f'turn-{turn:03d}.json');initial=read(folder/'turn-001.json');world=read(folder/'initial-map.json');wp={p['index']:p for p in world['plots']};plots={p['index']:p for p in s['plots']};players={p['id']:p for p in s['players']};leaders={p['id']:p for p in initial['players']};qrows=[];pc={}
 for pid,p in leaders.items():
  cities=[c for c in s['cities'] if c['player']==pid];owned=[x for x in s['plots'] if x['owner']==pid];pc[pid]={'player':pid,'leader':p['leader'],'civ':p['civ'],'cities':len(cities),'population':sum(c['population'] for c in cities),'improved_plots':sum(bool(x.get('improvement')) and not x['pillaged'] for x in owned),'completed':Counter(),'construction':Counter(),'pillaged':Counter(),'active_service_flags':Counter(),'service_buildings':Counter()}
  for c in cities:
   for key,v in c['properties'].items():
    if v>0:pc[pid]['active_service_flags'][key]+=v
   for b in c['buildings']:
    if '_SERVICE' in b['type'] and not b['pillaged']:pc[pid]['service_buildings'][b['type']]+=1
   for d in c['districts']:
    q=d.get('quarter')
    if q not in STAGES:continue
    pc[pid]['completed' if d['complete'] else 'construction'][q]+=1
    if d['pillaged']:pc[pid]['pillaged'][q]+=1
    if not d['complete']:continue
    qc=s['quarters'][q];base=set(qc['base']);spec=set(qc['spec']);neighbor=[]
    for idx in wp[d['plot']]['neighbors']:
     p=plots.get(idx,{});res=p.get('resource')
     if not res or defs[res]['ResourceClassType']=='RESOURCECLASS_ARTIFACT' or not visible(res,players[pid],defs):continue
     neighbor.append({'plot':idx,'resource':res,'owned':p.get('owner')==pid,'base':res in base,'spec':res in spec,'correct':res in base|spec,'bonus':defs[res]['ResourceClassType']=='RESOURCECLASS_BONUS','improved':bool(p.get('improvement')) and not p.get('pillaged',False)})
    own=[x for x in neighbor if x['owned']];bs=active(c)
    row={'player':pid,'city':c['name'],'quarter':q,'plot':d['plot'],'pillaged':d['pillaged'],'correct_owned':sum(x['correct'] for x in own),'base_owned':sum(x['base'] for x in own),'spec_owned':sum(x['spec'] for x in own),'incorrect_owned':sum(not x['correct'] for x in own),'incorrect_bonus_owned':sum(x['bonus'] and not x['correct'] for x in own),'correct_all_visible':sum(x['correct'] for x in neighbor),'incorrect_all_visible':sum(not x['correct'] for x in neighbor),'correct_improved':sum(x['correct'] and x['improved'] for x in own),'correct_unimproved_or_pillaged':sum(x['correct'] and not x['improved'] for x in own),'sales':d['site']['sales'],'noncenter_sales':sum(plots.get(i,{}).get('district') not in (None,'DISTRICT_CITY_CENTER') for i in d['site']['sales_plots']),'resources':neighbor}
    for stage,bts in enumerate(STAGES[q],2):row['stage'+str(stage)]=bool(bs.intersection(bts))
    row['active_services']={k:v for k,v in c['properties'].items() if k.startswith('CSC_'+q+'_') and v>0}
    qrows.append(row)
 aggregates={}
 for q in STAGES:
  rows=[x for x in qrows if x['quarter']==q];n=len(rows);fields=('correct_owned','base_owned','spec_owned','incorrect_owned','incorrect_bonus_owned','correct_all_visible','incorrect_all_visible','correct_improved','correct_unimproved_or_pillaged')
  totals=sums(rows,fields);aggregates[q]={'completed':n,'totals':totals,'means':{k:totals[k]/n if n else 0 for k in fields},'zero_correct_owned':sum(x['correct_owned']==0 for x in rows),'zero_any_visible_resources':sum(x['correct_all_visible']+x['incorrect_all_visible']==0 for x in rows),'only_incorrect_owned_resources':sum(x['correct_owned']==0 and x['incorrect_owned']>0 for x in rows),'wrong_bonus_and_no_base':sum(x['incorrect_bonus_owned']>0 and x['base_owned']==0 for x in rows),'base_support':sum(x['base_owned']>0 for x in rows),'both_support':sum(x['base_owned']>0 and x['spec_owned']>0 for x in rows),'any_sales':sum(x['sales']>0 for x in rows),'noncenter_sales':sum(x['noncenter_sales']>0 for x in rows),'with_active_service_flag':sum(bool(x['active_services']) for x in rows),'pillaged':sum(x['pillaged'] for x in rows),**{'stage'+str(k):sum(x['stage'+str(k)] for x in rows) for k in (2,3,4)}}
  for pid in pc:
   rr=[x for x in rows if x['player']==pid];pc[pid].setdefault('adjacency',{})[q]={'quarters':len(rr),'correct_owned':sum(x['correct_owned'] for x in rr),'incorrect_owned':sum(x['incorrect_owned'] for x in rr),'base_supported':sum(x['base_owned']>0 for x in rr)}
 services=Counter();buildings=Counter()
 for x in pc.values():services.update(x['active_service_flags']);buildings.update(x['service_buildings'])
 analysis=analyze(folder,turn)
 blockers={}
 for q in STAGES:
  for st in (2,3,4):
   rows=[x for x in analysis['service_opportunities'] if x['quarter']==q and x['stage']==st];blockers[q+str(st)]={'quarters':len(rows),'civic_unlocked':sum(x['civic_unlocked'] for x in rows),'source_building':sum(x['source_building'] for x in rows),'owned_materials':sum(x['owned_materials'] for x in rows),'improved_materials':sum(x['improved_materials'] for x in rows),'nearby_venue':sum(x['nearby_venue'] for x in rows),'all_recorded_conditions':sum(all(x[k] for k in ('civic_unlocked','source_building','improved_materials','nearby_venue')) for x in rows),'active_source_flags':sum(x['source_activation'] for x in rows)}
 assert sum(v['completed']['BAKERS'] for v in pc.values())==aggregates['BAKERS']['completed']
 return {'turn':turn,'players':list(pc.values()),'quarters':aggregates,'quarter_rows':qrows,'active_service_flags':services,'service_buildings':buildings,'unique_cities_with_active_flags':sum(any(v>0 for v in c['properties'].values()) for c in s['cities']),'service_gate_counts':blockers}

def replacement_audit(folder,turn,defs):
 final=read(folder/f'turn-{turn:03d}.json');world={p['index']:p for p in read(folder/'initial-map.json')['plots']};snaps=[]
 for p in folder.glob('turn-*.json'):
  s=read(p)
  if s['turn']<=turn:snaps.append({'turn':s['turn'],'events':len(s['events']),'plots':{p['index']:p for p in s['plots']},'state':s})
 snaps.sort(key=lambda x:(x['turn'],x['events']));events=final['events'];seen=set();placements=[];cases=[];already_gone=[];retained=[]
 for i,e in enumerate(events):
  if e['event']!='district':continue
  key=(e['plot'],e['district'])
  if key in seen:continue
  seen.add(key)
  candidates=[x for x in snaps if x['turn']<=e['turn'] and x['events']<=i]
  if not candidates:continue
  before=max(candidates,key=lambda x:(x['turn'],x['events']));state=dict(before['plots'].get(e['plot'],{}))
  if state.get('district'):continue # prior existing district: capture/recreation, not a new build
  row={'turn':e['turn'],'player':e['player'],'plot':e['plot'],'district':e['district'],'quarter':e.get('quarter'),'pre_snapshot_turn':before['turn']};placements.append(row)
  last_turn=before['turn'];last_source='snapshot'
  for ev in events[before['events']:i]:
   if ev['event']=='improvement' and ev['plot']==e['plot']:
    state.update(resource=ev.get('resource'),improvement=ev.get('improvement'),owner=ev.get('owner'),pillaged=False);last_turn=ev['turn'];last_source='improvement_event'
  resource=state.get('resource')
  if not resource:
   if world[e['plot']].get('resource'):already_gone.append({**row,'initial_resource':world[e['plot']]['resource']})
   continue
  afters=[x for x in snaps if x['events']>i and x['turn']>=e['turn']]
  after=min(afters,key=lambda x:(x['turn'],x['events'])) if afters else None;post=(after['plots'].get(e['plot'],{}) if after else {})
  detail={**row,'resource':resource,'resource_class':defs[resource]['ResourceClassType'],'last_known_improvement':state.get('improvement'),'last_known_pillaged':state.get('pillaged',False),'last_observed_turn':last_turn,'observation_age':e['turn']-last_turn,'evidence_source':last_source,'post_snapshot_turn':after['turn'] if after else None,'post_resource':post.get('resource'),'post_district':post.get('district'),'known_support_for':[]}
  for c in before['state']['cities']:
   if c['player']!=e['player']:continue
   for q in c['districts']:
    name=q.get('quarter')
    if name in STAGES and e['plot'] in world[q['plot']]['neighbors'] and resource in (set(before['state']['quarters'][name]['base'])|set(before['state']['quarters'][name]['spec'])):
     detail['known_support_for'].append({'quarter':name,'quarter_plot':q['plot'],'complete':q['complete'],'pillaged':q['pillaged']})
  if post.get('resource')==resource:retained.append(detail)
  elif post.get('district'):cases.append(detail)
  else:detail['post_state_unconfirmed']=True;cases.append(detail)
 def summary(items):
  return {'count':len(items),'improved_last_seen':sum(bool(x['last_known_improvement']) and not x['last_known_pillaged'] for x in items),'pillaged_last_seen':sum(bool(x['last_known_improvement']) and x['last_known_pillaged'] for x in items),'unimproved_last_seen':sum(not x['last_known_improvement'] for x in items),'quarters':sum(bool(x['quarter']) for x in items),'nonquarter_districts':sum(not x['quarter'] for x in items),'supported_matching_existing_quarter':sum(bool(x['known_support_for']) for x in items),'recent_improved_evidence_age_0_or_1':sum(bool(x['last_known_improvement']) and not x['last_known_pillaged'] and x['observation_age']<=1 for x in items),'resources':dict(Counter(x['resource'] for x in items))}
 all_noncenters=[x for x in cases if x['district']!='DISTRICT_CITY_CENTER'];retained_noncenters=[x for x in retained if x['district']!='DISTRICT_CITY_CENTER']
 major_ids={p['id'] for p in final['players']}
 noncenters=[x for x in all_noncenters if x['player'] in major_ids and x['resource_class']!='RESOURCECLASS_ARTIFACT' and x['district']!='DISTRICT_WONDER']
 return {'scope':'Major-player districts only; excludes City Centers, Wonders and artifact sites. Raw excluded cases retained separately.','excluded_cases':[x for x in all_noncenters if x not in noncenters],'summary':summary(noncenters),'by_period':{label:summary([x for x in noncenters if lo<=x['turn']<=hi]) for label,lo,hi in [('1-100',1,100),('101-150',101,150),('151-225',151,225)]},'by_placing_district':{d:summary([x for x in noncenters if x['district']==d]) for d in sorted({x['district'] for x in noncenters})},'by_player':{str(p):summary([x for x in noncenters if x['player']==p]) for p in range(6)},'cases':noncenters,'resource_retained_under_district':retained_noncenters,'original_resource_already_absent_before_placement':[x for x in already_gone if x['district']!='DISTRICT_CITY_CENTER'],'observed_new_quarter_placements_by_player':{str(pid):{q:sum(x['player']==pid and x.get('quarter')==q for x in placements) for q in STAGES} for pid in range(6)},'settling_on_resource_cases':len([x for x in cases if x['district']=='DISTRICT_CITY_CENTER']),'limitation':'Last-observed state, not an immediately-before removal hook. Harvest/removal events were not recorded; intervening harvesting cannot always be excluded. Districts/captures deduplicated; gap51-67 remains.'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--current',type=Path,required=True);p.add_argument('--previous',type=Path,required=True);p.add_argument('--database',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();c=sqlite3.connect(a.database.as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row;defs={r['ResourceType']:dict(r) for r in c.execute('SELECT ResourceType,ResourceClassType,PrereqTech,PrereqCivic FROM Resources')};c.close()
 data={label:{str(t):analyze_detail(folder,t,defs) for t in (200,225)} for label,folder in [('current',a.current),('previous',a.previous)]};data['replacements']={label:replacement_audit(folder,225,defs) for label,folder in [('current',a.current),('previous',a.previous)]};a.output.mkdir(exist_ok=True,parents=True);(a.output/'details.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8');shutil.copy2(__file__,a.output/Path(__file__).name)
 compact={'players225':data['current']['225']['players'],'adjacency225':data['current']['225']['quarters'],'service_flags225':data['current']['225']['active_service_flags'],'service_buildings225':data['current']['225']['service_buildings'],'service_gates225':data['current']['225']['service_gate_counts'],'replacements_current':{k:v for k,v in data['replacements']['current'].items() if k not in ('cases','resource_retained_under_district','original_resource_already_absent_before_placement')},'retained_resource_districts':len(data['replacements']['current']['resource_retained_under_district']),'resource_already_absent':len(data['replacements']['current']['original_resource_already_absent_before_placement'])}
 print(json.dumps(compact))
if __name__=='__main__':main()
