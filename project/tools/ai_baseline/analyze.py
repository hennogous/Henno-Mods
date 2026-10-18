"""Aggregate recorded natural-play CSC decisions; never connects to the game."""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
from statistics import median

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def fraction(n,d):return f'{n}/{d} ({100*n/d:.0f}%)' if d else '0/0'
def rows(value):return value if isinstance(value,list) else []
def types(city):return {b['type'] for b in city['buildings'] if not b['pillaged']}
STAGES={'BAKERS':[['BUILDING_CSC_BAKERS_WATER_MILL','BUILDING_CSC_BAKERS_WIND_MILL'],['BUILDING_CSC_BAKERS_BAKERY'],['BUILDING_CSC_BAKERS_CAFE']],
        'TAILORS':[['BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'],['BUILDING_CSC_TAILORS_TAILOR'],['BUILDING_CSC_TAILORS_FASHION_HOUSE']]}
SERVICE_GATES={
 'BAKERS':[(2,'CIVIC_FEUDALISM',['BUILDING_GRANARY'],'CSC_BAKERS_STAGE_2_EFFECT_GROWTH'),(3,'CIVIC_MEDIEVAL_FAIRES',['BUILDING_MARKET'],'CSC_BAKERS_STAGE_3_EFFECT_HOUSING'),(4,'CIVIC_URBANIZATION',['BUILDING_ZOO','BUILDING_FERRIS_WHEEL'],'CSC_BAKERS_STAGE_4_EFFECT_TOURISM')],
 'TAILORS':[(2,'CIVIC_NAVAL_TRADITION',['BUILDING_LIGHTHOUSE'],'CSC_TAILORS_STAGE_2_EFFECT_PRODUCTION'),(3,'CIVIC_DIVINE_RIGHT',['BUILDING_TEMPLE'],'CSC_TAILORS_STAGE_3_EFFECT_FAITH'),(4,'CIVIC_OPERA_BALLET',['BUILDING_AMPHITHEATER','BUILDING_BOLSHOI_THEATRE','BUILDING_BROADWAY','BUILDING_SYDNEY_OPERA_HOUSE'],'CSC_TAILORS_STAGE_4_EFFECT_TOURISM')]}

def distance(a,b,width):
    def cube(x,y):q=x-(y-(y&1))//2;return q,-q-y,y
    x=cube(a['x'],a['y'])
    return min(max(abs(v-w) for v,w in zip(x,cube(b['x']+shift,b['y']))) for shift in (-width,0,width))

def analyze(folder,turn=200):
    s=read(folder/f'turn-{turn:03d}.json');initial=read(folder/'turn-001.json');settings=read(folder/'settings.json');pids={p['id'] for p in initial['players']}
    ds=[(c,d) for c in s['cities'] for d in c['districts'] if d.get('quarter')];complete=[(c,d) for c,d in ds if d['complete']]
    # DistrictAddedToMap also fires when capture recreates existing districts.
    # Only the first observed appearance of each plot/type is a placement choice.
    seen=set();events=[];transfers=[]
    for e in s['events']:
        if e['event']=='district':
            identity=(e['plot'],e['district'])
            if identity in seen:transfers.append(e);continue
            seen.add(identity)
        if e.get('player',e.get('owner')) in pids:events.append(e)
    placed=[e for e in events if e.get('quarter')]
    improvements=[e for e in events if e['event']=='improvement']
    placed_lookup={(e['player'],e['plot']):e for e in placed}
    totals=Counter(cities=len(s['cities']),players=len(s['players']),quarters=len(ds),completed=len(complete),placements=len(placed))
    byq={};details=[];choices=[];material_unique={};timing=[];plot_by_id={p['index']:p for p in s['plots']}
    unlocked={p['id'] for p in s['players'] if 'CIVIC_CRAFTSMANSHIP' in p['civics']}
    for q in STAGES:
        cur=[(c,d) for c,d in complete if d['quarter']==q];pl=[e for e in placed if e['quarter']==q]
        v=Counter(completed=len(cur),placed=len(pl))
        for c,d in cur:
            site=d['site'];bs=types(c)
            v['pillaged']+=d['pillaged']
            for label,condition in [('base',site['base']>0),('spec',site['spec']>0),('both',site['base']>0 and site['spec']>0),('sales',site['sales']>0),('all_three',site['base']>0 and site['spec']>0 and site['sales']>0),('zero_material',site['base']==0 and site['spec']==0),('both_improved',site['base_improved']>0 and site['spec_improved']>0)]:v[label]+=condition
            v['both_visible_any_owner']+=site['base_any']>0 and site['spec_any']>0
            v['city_center_sales']+=any(plot_by_id.get(p,{}).get('district')=='DISTRICT_CITY_CENTER' for p in site['sales_plots'])
            v['non_center_sales']+=any(plot_by_id.get(p,{}).get('district') not in (None,'DISTRICT_CITY_CENTER') for p in site['sales_plots'])
            for i,stage in enumerate(STAGES[q],2):v['stage'+str(i)]+=bool(bs.intersection(stage))
            detail={'game':folder.name,'player':c['player'],'city':c['name'],'quarter':q,'plot':d['plot'],'population':c['population'],'pillaged':d['pillaged'],'base':site['base'],'spec':site['spec'],'sales':site['sales'],'base_improved':site['base_improved'],'spec_improved':site['spec_improved'],'placed_turn':placed_lookup.get((c['player'],d['plot']),{}).get('turn')}
            details.append(detail)
            for m in site['materials']:
                if m['owner']==c['player']:material_unique[(q,c['player'],m['plot'])]=m
        for e in pl:
            site=e['site'];cached=e.get('previous_candidates') or {};options=rows(cached.get('sites'))
            comparable=options and e['turn']-cached.get('turn',-100)<=1
            choice={'game':folder.name,'player':e['player'],'quarter':q,'turn':e['turn'],'plot':e['plot'],'base':site['base'],'spec':site['spec'],'sales':site['sales'],'candidates':len(options),'cache_turn':cached.get('turn'),'same_turn_cache':cached.get('turn')==e['turn'],'selected_in_cache':any(x['plot']==e['plot'] for x in options)}
            if comparable:
                v['comparable']+=1
                both_options=[x for x in options if x['base']>0 and x['spec']>0]
                if both_options:v['both_available']+=1;v['both_chosen_when_available']+=site['base']>0 and site['spec']>0
                all_options=[x for x in both_options if x['sales']>0]
                if all_options:v['all_available']+=1;v['all_chosen_when_available']+=site['base']>0 and site['spec']>0 and site['sales']>0
                maxmat=max(x['base']+x['spec'] for x in options);choice['max_materials']=maxmat;choice['both_available']=bool(both_options);choice['all_available']=bool(all_options)
                v['max_material_chosen']+=site['base']+site['spec']>=maxmat
                if maxmat>0:v['material_opportunity']+=1;v['max_material_with_opportunity']+=site['base']+site['spec']>=maxmat
            choices.append(choice)
            for m in site['materials']:
                if m['owner']==e['player'] and not m.get('improvement'):
                    future=[i['turn'] for i in improvements if i['plot']==m['plot'] and i['turn']>=e['turn'] and i['owner']==e['player'] and i.get('resource')==m['resource']]
                    timing.append({'game':folder.name,'quarter':q,'quarter_plot':e['plot'],'resource_plot':m['plot'],'resource':m['resource'],'category':m['category'],'quarter_turn':e['turn'],'improved_turn':min(future) if future else None,'exposure_turns':turn-e['turn']})
        # Owned, native-plot-legal current opportunities where no Quarter is placed.
        opts=[o for o in s['options'] if o['quarter']==q and o['player'] in unlocked]
        v['unbuilt_city_options']=len(opts);v['unbuilt_both_opportunity']=sum(any(x['base']>0 and x['spec']>0 for x in rows(o['sites'])) for o in opts)
        v['unbuilt_all_opportunity']=sum(any(x['base']>0 and x['spec']>0 and x['sales']>0 for x in rows(o['sites'])) for o in opts)
        v['unbuilt_both_visible_any_owner']=sum(any(x['base_any']>0 and x['spec_any']>0 for x in rows(o['sites'])) for o in opts)
        mats=[m for (qq,_,_),m in material_unique.items() if qq==q];v['adjacent_resources']=len(mats);v['adjacent_improved']=sum(bool(m.get('improvement')) and not m['pillaged'] for m in mats)
        byq[q]=dict(v)
    # Customer order is observed at initial placement, including incomplete Quarters.
    customer=[]
    for e in events:
        if e['event']!='district' or e.get('quarter') or e['district']=='DISTRICT_CITY_CENTER':continue
        for q,neighbors in (e.get('quarter_sites') or {}).items():
            prior=[x for x in placed if x['player']==e['player'] and x['quarter']==q and x['turn']<e['turn']]
            if prior:
                cached=(e.get('customer_candidates') or {}).get(q) or {};options=rows(cached.get('sites'))
                customer.append({'game':folder.name,'player':e['player'],'quarter':q,'district':e['district'],'turn':e['turn'],'adjacent':bool(neighbors),'quarter_count_before':len(prior),'cache_turn':cached.get('turn'),'adjacency_option':any(x.get('quarters',0)>0 for x in options),'comparable':bool(options) and e['turn']-cached.get('turn',-100)<=1})
    services=Counter();service_cities=Counter()
    for c in s['cities']:
        for key,value in (c.get('properties') or {}).items():
            if value>0:services[key]+=value;service_cities[key]+=1
    hidden=Counter(b['type'] for c in s['cities'] for b in c['buildings'] if '_SERVICE' in b['type'] and not b['pillaged'])
    service_opportunities=[];plots={p['index']:p for p in s['plots']};players={p['id']:p for p in s['players']}
    reference_path=folder.parent/'mechanics-reference.json';reference=read(reference_path) if reference_path.exists() else {}
    defs={b['BuildingType']:b for b in reference.get('buildings',[])};building_opportunities=[]
    improvement_comparison=[]
    for q in STAGES:
        classes=s['quarters'][q];adjacent={(pid,index) for (qq,pid,index) in material_unique if qq==q};enabled=set()
        for c,d in complete:
            if d['quarter']!=q:continue
            bs=types(c)
            for m in d['site']['materials']:
                required=STAGES[q][0] if m['category']=='base' else STAGES[q][2]
                if m['owner']==c['player'] and bs.intersection(required):enabled.add((c['player'],m['plot']))
        for plot in s['plots']:
            if plot['owner'] not in players or not plot.get('resource'):continue
            resource=plot['resource'];cat='base' if resource in classes['base'] else 'spec' if resource in classes['spec'] else None
            if not cat:continue
            key=(plot['owner'],plot['index']);near_city=any(c['player']==plot['owner'] and distance(c,plot,s['width'])<=3 for c in s['cities'])
            if key not in adjacent and not near_city:continue
            improvement_comparison.append({'game':folder.name,'quarter':q,'player':plot['owner'],'plot':plot['index'],'resource':resource,'category':cat,'adjacent_to_quarter':key in adjacent,'relevant_building_present':key in enabled,'within_workable_radius':near_city,'improved':bool(plot.get('improvement')) and not plot['pillaged']})
    for c,d in complete:
        q=d['quarter'];bs=types(c);pc=players[c['player']]
        for stage,buildings in enumerate(STAGES[q],2):
            def unlocked(bt):
                b=defs.get(bt,{})
                return bool(b) and (not b['PrereqTech'] or b['PrereqTech'] in pc['techs']) and (not b['PrereqCivic'] or b['PrereqCivic'] in pc['civics'])
            research=any(unlocked(bt) for bt in buildings)
            source=stage==2 or bool(bs.intersection(STAGES[q][0]))
            building_opportunities.append({'game':folder.name,'player':c['player'],'city':c['name'],'quarter':q,'stage':stage,'research_unlocked':research,'stage2_prerequisite':source,'built':bool(bs.intersection(buildings))})
    retention=[]
    for c,d in complete:
        placed_event=placed_lookup.get((c['player'],d['plot']))
        if not placed_event:continue
        for m in placed_event['site']['materials']:
            if m['owner']!=c['player']:continue
            final=plots.get(m['plot'],{})
            retention.append({'game':folder.name,'quarter':d['quarter'],'player':c['player'],'quarter_plot':d['plot'],'resource_plot':m['plot'],'initial_resource':m['resource'],'final_resource':final.get('resource'),'resource_retained':final.get('resource')==m['resource'],'ownership_retained':final.get('owner')==c['player'],'final_district':final.get('district')})
    for c,d in complete:
        q=d['quarter'];bs=types(c);site=d['site'];pc=players[c['player']]
        for stage,civic,venues,prop in SERVICE_GATES[q]:
            nearby=[]
            for recipient in s['cities']:
                if recipient['player']!=c['player']:continue
                for b in recipient['buildings']:
                    if b['type'] in venues and not b['pillaged'] and b['plot'] in plots and distance(d,plots[b['plot']],s['width'])==1:nearby.append(b['type'])
            service_opportunities.append({'game':folder.name,'player':c['player'],'city':c['name'],'quarter':q,'stage':stage,'civic':civic,'civic_unlocked':civic in pc['civics'],'source_building':bool(bs.intersection(STAGES[q][stage-2])),'owned_materials':site['base']>0 and (stage<4 or site['spec']>0),'improved_materials':site['base_improved']>0 and (stage<4 or site['spec_improved']>0),'nearby_venue':bool(nearby),'venues':';'.join(nearby),'source_activation':(c.get('properties') or {}).get(prop,0)>0})
    snapshots=[]
    for p in sorted(folder.glob('turn-*.json')):
        snap=read(p);snapshots.append({'turn':snap['turn'],'cities':len(snap['cities']),'quarters':sum(bool(d.get('quarter')) for c in snap['cities'] for d in c['districts']),'completed_quarters':sum(bool(d.get('quarter')) and d['complete'] for c in snap['cities'] for d in c['districts']),'service_sources':sum(v>0 for c in snap['cities'] for v in (c.get('properties') or {}).values())})
    return {'game':folder.name,'settings':settings,'totals':dict(totals),'quarters':byq,'services_source_counts':dict(services),'service_source_cities':dict(service_cities),'hidden_service_buildings':dict(hidden),'service_opportunities':service_opportunities,'building_opportunities':building_opportunities,'improvement_comparison':improvement_comparison,'material_retention':retention,'details':details,'choices':choices,'improvement_timing':timing,'customer_choices':customer,'timeline':snapshots,'leaders':[p['leader'] for p in initial['players']],'alive_players':[p['id'] for p in s['players']],'observer_errors':s['errors'],'repeated_district_appearances_excluded':len(transfers)}

def output_csv(path,values):
    if not values:return
    fields=list(dict.fromkeys(k for r in values for k in r))
    with path.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(values)

def strategy_profiles(folder,game):
    # Native AI logs append across games; isolate the final monotonic turn segment.
    segment=[];previous=-1
    with (folder/'logs/AI_Victories.csv').open(encoding='utf-8-sig') as f:
        for row in csv.reader(f):
            try:turn=int(row[0]);pid=int(row[1])
            except (ValueError,IndexError):continue
            if turn<previous:segment=[]
            segment.append((turn,pid,row[2].strip(),row[3].strip()));previous=turn
    last={}
    for turn,pid,strategy,status in segment:last[(pid,strategy)]=status
    result=[]
    for pid,leader in enumerate(game['leaders']):
        if pid not in game['alive_players']:continue
        flags=[s.removeprefix('VICTORY_STRATEGY_').removesuffix('_VICTORY') for (p,s),status in last.items() if p==pid and s.startswith('VICTORY_STRATEGY_') and status=='Following']
        quarters=[d for d in game['details'] if d['player']==pid]
        result.append({'game':folder.name,'player':pid,'leader':leader,'active_victory_flags':';'.join(sorted(flags)),'bakers':sum(d['quarter']=='BAKERS' for d in quarters),'tailors':sum(d['quarter']=='TAILORS' for d in quarters)})
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--turn',type=int,default=200);a=p.parse_args()
    games=[analyze(f,a.turn) for f in sorted(a.output.glob('game-*')) if (f/'complete.json').exists()]
    for g in games:g['strategy_profiles']=strategy_profiles(a.output/g['game'],g)
    report={'games':games,'completed_games':len(games),'endpoint_turn':a.turn}
    (a.output/'analysis.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    for name in ('details','choices','improvement_timing','customer_choices','service_opportunities','building_opportunities','material_retention','improvement_comparison','strategy_profiles'):
        output_csv(a.output/(name+'.csv'),[r for g in games for r in g[name]])
    text=['# CSC AI baseline results','',f'{len(games)} completed games at turn {a.turn}. CSC with standard game AI; Small Continents, six civilizations, nine city states, Standard speed, Prince difficulty. No AI tuning or artificial gameplay setup.','',
          '## Games','', '| Game | Cities | Completed Bakers | Completed Tailors | Active supply stages |','|---|---:|---:|---:|---:|']
    for g in games:text.append(f'| {g["game"]} | {g["totals"]["cities"]} | {g["quarters"]["BAKERS"]["completed"]} | {g["quarters"]["TAILORS"]["completed"]} | {sum(g["service_source_cities"].values())} |')
    text+=['','## Quarter placement and development','',f'Metrics below use completed Quarters at turn {a.turn}. Materials must be visible and player-owned. Improvement counts deduplicate plots within each Quarter type and player.','',
           '| Metric | Bakers | Tailors |','|---|---:|---:|']
    aggregate={q:sum((Counter(g['quarters'][q]) for g in games),Counter()) for q in STAGES}
    for label,numerator,denominator in [('Completed Quarters','completed',None),('Adjacent base material','base','completed'),('Adjacent specialty material','spec','completed'),('Both material classes','both','completed'),('Sales district adjacent','sales','completed'),('Sales district other than City Center','non_center_sales','completed'),('Both materials and sales district','all_three','completed'),('No material adjacency','zero_material','completed'),('Both classes improved','both_improved','completed'),('Stage 2 building present','stage2','completed'),('Stage 3 building present','stage3','completed'),('Stage 4 building present','stage4','completed'),('Adjacent owned material plots improved','adjacent_improved','adjacent_resources'),('Both classes chosen when available at player-turn start','both_chosen_when_available','both_available'),('Both classes and sales chosen when available','all_chosen_when_available','all_available'),('Maximum material count chosen when a material site existed','max_material_with_opportunity','material_opportunity'),('Unlocked cities without Quarter with a current both-material site','unbuilt_both_opportunity','unbuilt_city_options')]:
        cells=[fraction(aggregate[q][numerator],aggregate[q][denominator]) if denominator else str(aggregate[q][numerator]) for q in STAGES]
        text.append('| '+label+' | '+' | '.join(cells)+' |')
    text+=['','## Customer district follow-up','', '| Quarter | Later customer placements | Adjacent placements | Adjacent chosen when an owned legal option existed |','|---|---:|---:|---:|']
    for q in STAGES:
        v=[v for g in games for v in g['customer_choices'] if v['quarter']==q];comparable=[x for x in v if x['comparable'] and x['adjacency_option']]
        text.append(f'| {q.title()} | {len(v)} | {sum(x["adjacent"] for x in v)} | {fraction(sum(x["adjacent"] for x in comparable),len(comparable))} |')
    text+=['','A later customer placement means its owner had already placed that Quarter in an earlier turn. City Centers are excluded. These are descriptive choices, not proof of AI intent.','',
           '## Material improvement follow-up','', f'| Quarter | Initially unimproved owned materials beside new Quarters | Improved later by turn {a.turn} | Median wait among improved |','|---|---:|---:|---:|']
    for q in STAGES:
        v=[v for g in games for v in g['improvement_timing'] if v['quarter']==q];finished=[x for x in v if x['improved_turn'] is not None];waits=[x['improved_turn']-x['quarter_turn'] for x in finished]
        text.append(f'| {q.title()} | {len(v)} | {fraction(len(finished),len(v))} | {median(waits) if waits else "n/a"} |')
    text+=['','This follow-up is counted per resource–Quarter relationship; late placements have less time to receive improvements. It is not a matched test of builder priorities.','',
           '| Quarter | Adjacent materials within workable radius | Adjacent with relevant source building | Non-adjacent materials within workable radius |','|---|---:|---:|---:|']
    for q in STAGES:
        v=[v for g in games for v in g['improvement_comparison'] if v['quarter']==q and v['within_workable_radius']];adj=[x for x in v if x['adjacent_to_quarter']];enabled=[x for x in adj if x['relevant_building_present']];other=[x for x in v if not x['adjacent_to_quarter']]
        text.append(f'| {q.title()} | {fraction(sum(x["improved"] for x in adj),len(adj))} | {fraction(sum(x["improved"] for x in enabled),len(enabled))} | {fraction(sum(x["improved"] for x in other),len(other))} |')
    text+=['','These are descriptive final-state comparisons within three tiles of an owner city. They are not matched for city age, terrain, resource type or time exposed to a Quarter. The relevant building is stage 2 for base materials and stage 4 for specialty materials.','',
           '## Material retention','', '| Quarter | Initially owned material relationships for surviving same-owner Quarters | Resource still present | Resource replaced by district |','|---|---:|---:|---:|']
    for q in STAGES:
        v=[v for g in games for v in g['material_retention'] if v['quarter']==q]
        text.append(f'| {q.title()} | {len(v)} | {sum(x["resource_retained"] for x in v)} | {sum(not x["resource_retained"] and bool(x["final_district"]) for x in v)} |')
    text+=['',f'These comparisons establish that a resource was present at Quarter placement and absent under a district at turn {a.turn}. They do not identify the AI reasoning behind clearing it.','',
           '## Building progression','', '| Quarter and stage | Research unlocked | Stage 2 prerequisite also present | Building present among those candidates |','|---|---:|---:|---:|']
    for q in STAGES:
        for stage in (2,3,4):
            v=[v for g in games for v in g['building_opportunities'] if v['quarter']==q and v['stage']==stage];u=[x for x in v if x['research_unlocked']];eligible=[x for x in u if x['stage2_prerequisite']]
            text.append(f'| {q.title()} stage {stage} | {len(u)}/{len(v)} | {len(eligible)} | {sum(x["built"] for x in eligible)} |')
    text+=['','Research unlocks come from the captured runtime gameplay database. These counts do not test affordability or every production restriction.','',
           '## Services','', f'| Supply activation property | City observations at turn {a.turn} |','|---|---:|']
    services=sum((Counter(g['service_source_cities']) for g in games),Counter())
    for key,value in sorted(services.items()):text.append(f'| `{key}` | {value} |')
    text+=['','| Quarter and stage | Civic unlocked | Source building also present | Improved material gate also met | Required venue also adjacent |','|---|---:|---:|---:|---:|']
    for q in STAGES:
        for stage in (2,3,4):
            v=[v for g in games for v in g['service_opportunities'] if v['quarter']==q and v['stage']==stage];u=[x for x in v if x['civic_unlocked']];b=[x for x in u if x['source_building']];m=[x for x in b if x['improved_materials']];h=[x for x in m if x['nearby_venue']]
            text.append(f'| {q.title()} stage {stage} | {len(u)}/{len(v)} | {len(b)} | {len(m)} | {len(h)} |')
    text+=['','`hidden_service_buildings` in analysis.json separately records actual Service buildings. The properties describe supply activation; they do not prove the AI planned to obtain the Service.','',
           '## Quarter ownership and native victory strategy flags','', f'| Active native flag at turn {a.turn} | Civilization observations | Completed Bakers owned | Completed Tailors owned |','|---|---:|---:|---:|']
    profiles=[v for g in games for v in g['strategy_profiles']]
    for flag in ('CULTURAL','RELIGIOUS','SCIENCE','MILITARY','DIPLOMATIC'):
        v=[v for v in profiles if flag in v['active_victory_flags'].split(';')]
        text.append(f'| {flag.title()} | {len(v)} | {sum(x["bakers"] for x in v)} | {sum(x["tailors"] for x in v)} |')
    text+=['','Flags come from the final game segment in AI_Victories.csv, using the latest status for each strategy. A civilization can follow several flags simultaneously. These are overlapping descriptive groups, not exclusive victory commitments or evidence of CSC-specific intent.','',
           '## Interpretation limits','',
           '- The sample covers the implemented Bakers and Tailors Quarters. Five games are a descriptive baseline, not a causal experiment.',
           '- Candidate comparisons use the most recent player-turn-start scan, at most one turn old, and native plot placement checks on already owned tiles. They do not include future tile purchases, tile swaps, affordability, or full production eligibility. Ownership or occupied plots can change during a turn.',
           f'- The final snapshot is at the beginning of turn {a.turn}, following {a.turn-1} advances from turn 1. District events include placement before completion; final placement statistics use completed districts.',
           '- Capture, pillage, resource discovery and border expansion can change final adjacency. Placement-time choices are recorded separately.',
           '- A setup pilot generated a Duel map and is excluded under pilot-duel-excluded. Only game folders with complete.json enter this analysis.','',
           'Raw evidence: turn snapshots, exact district/improvement events, per-game saves and logs, installed gameplay hashes, fixed seed pairs and command transcripts are in this output folder.']
    (a.output/'report.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    print('Completed games:',len(games))
    for g in games:print(g['game'],g['totals'],g['quarters'])

if __name__=='__main__':main()


