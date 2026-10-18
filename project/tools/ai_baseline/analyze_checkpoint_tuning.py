"""Compare archived checkpoints without changing historical tools or source pins.

Parameter-aware copies of base_opportunities, summarize and extra preserve the
historical metric definitions. Read original snapshots directly, never rename
or fabricate an endpoint. An interrupted run remains incomplete at turn 250.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
from statistics import median
from analyze import analyze, read, output_csv, fraction

def base_opportunities(folder,game,turn):
    """Separate useful Base access from Specialty-only alternatives."""
    final=json.loads((folder/f'turn-{turn:03d}.json').read_text(encoding='utf-8'))
    initial=json.loads((folder/'turn-001.json').read_text(encoding='utf-8'))
    majors={p['id'] for p in initial['players']};seen=set();result=[]
    for e in final['events']:
        if e['event']!='district':continue
        identity=(e['plot'],e.get('district'))
        if identity in seen:continue
        seen.add(identity)
        q=e.get('quarter')
        if q not in ('BAKERS','TAILORS') or e['player'] not in majors:continue
        cache=e.get('previous_candidates') or {};sites=cache.get('sites',[])
        if not isinstance(sites,list) or not sites or not 0<=e['turn']-cache.get('turn',-100)<=1:continue
        chosen=e['site'];base=any(x['base']>0 for x in sites)
        base_sales=any(x['base']>0 and x['sales']>0 for x in sites)
        v=game['quarters'][q]
        flags={'base_available':base,'base_chosen_when_available':base and chosen['base']>0,
            'base_sales_available':base_sales,'base_sales_chosen_when_available':base_sales and chosen['base']>0 and chosen['sales']>0,
            'no_base_chosen_when_available':base and chosen['base']==0,
            'no_material_chosen_when_base_available':base and chosen['base']==0 and chosen['spec']==0}
        for key,value in flags.items():v[key]=v.get(key,0)+int(value)
        result.append({'game':game['game'],'quarter':q,'player':e['player'],'plot':e['plot'],'turn':e['turn'],
            'candidates':len(sites),'chosen_base':chosen['base'],'chosen_spec':chosen['spec'],'chosen_sales':chosen['sales'],**flags})
    return result

def summarize(folder,turn):
    game=analyze(folder,turn)
    game['base_placement_choices']=base_opportunities(folder,game,turn)
    s=read(folder/f'turn-{turn:03d}.json')
    majors={p['id'] for p in read(folder/'turn-001.json')['players']}
    game['population']=sum(c['population'] for c in s['cities'])
    game['owned_improved_plots']=sum(p['owner'] in majors and bool(p.get('improvement')) and not p['pillaged'] for p in s['plots'])
    for q,v in game['quarters'].items():
        for cat in ('base','spec'):
            plots=[p for p in game['improvement_comparison'] if p['quarter']==q and p['category']==cat and p['adjacent_to_quarter']]
            v[cat+'_plots']=len(plots);v[cat+'_plots_improved']=sum(p['improved'] for p in plots)
        sales=[p for p in game['customer_choices'] if p['quarter']==q and p['comparable'] and p['adjacency_option']]
        v['later_sales_options']=len(sales);v['later_sales_chosen']=sum(p['adjacent'] for p in sales)
        seen=set();available=chosen=0
        for e in s['events']:
            if e['event']!='district':continue
            identity=(e['plot'],e.get('district'))
            if identity in seen:continue
            seen.add(identity)
            if e.get('quarter')!=q or e['player'] not in majors:continue
            cache=e.get('previous_candidates') or {};sites=cache.get('sites') or []
            if not sites or not 0<=e['turn']-cache.get('turn',-100)<=1:continue
            if any(p['sales']>0 for p in sites):
                available+=1;chosen+=e['site']['sales']>0
        v['quarter_sales_options']=available;v['quarter_sales_chosen']=chosen
        lost={p['resource_plot'] for p in game['material_retention'] if p['quarter']==q and not p['resource_retained'] and p['final_district']}
        v['supporting_plots_under_districts']=len(lost)
        waits=[p['improved_turn']-p['quarter_turn'] for p in game['improvement_timing'] if p['quarter']==q and p['category']=='base' and p['improved_turn'] is not None]
        v['base_improvement_median_wait']=median(waits) if waits else None
    game['timeline']=[r for r in game['timeline'] if r['turn']<=turn]
    return game

def extra(folder, game, resources, turn):
    initial=read(folder/'turn-001.json'); final=read(folder/f'turn-{turn:03d}.json')
    majors={p['id'] for p in initial['players']}
    world={p['index']:p for p in read(folder/'initial-map.json')['plots']}
    plots={p['index']:p for p in final['plots']}
    river_choices=[]; seen=set(); proxy=[]
    for event in final['events']:
        if event['event']!='district':continue
        key=(event['plot'],event.get('district'))
        if key in seen:continue
        seen.add(key)
        if not event.get('quarter') or event['player'] not in majors:continue
        cache=event.get('previous_candidates') or {};sites=cache.get('sites') or []
        if not isinstance(sites,list) or not sites or not 0<=event['turn']-cache.get('turn',-100)<=1:continue
        selected=event['site']
        river_choices.append({'quarter':event['quarter'],'player':event['player'],
            'turn':event['turn'],'plot':event['plot'],'river_available':any(p['river'] for p in sites),
            'mixed_river_options':any(p['river'] for p in sites) and any(not p['river'] for p in sites),
            'river_chosen':selected['river'],
            'base_river_available':any(p['river'] and p['base']>0 for p in sites),
            'base_river_chosen':selected['river'] and selected['base']>0,
            'cache_age':event['turn']-cache['turn'],
            'selected_in_cache':any(p['plot']==event['plot'] for p in sites)})
    for city in final['cities']:
        for district in city['districts']:
            q=district.get('quarter')
            if not q or not district['complete']:continue
            base=set(final['quarters'][q]['base'])
            neighbors=world[district['plot']]['neighbors']
            deposits=[plots[n] for n in neighbors if n in plots and resources.get(plots[n].get('resource'))=='RESOURCECLASS_BONUS']
            proxy.append({'player':city['player'],'quarter':q,'plot':district['plot'],
                'river':district['site']['river'],'bonus_copies':len(deposits),
                'mapped_bonus_copies':sum(p['resource'] in base for p in deposits),
                'owned_mapped_bonus_copies':sum(p['resource'] in base and p['owner']==city['player'] for p in deposits),
                'actual_owned_base':district['site']['base'],
                'proxy_without_owned_base':bool(deposits) and district['site']['base']==0})
    for q,values in game['quarters'].items():
        values['supporting_plots_total']=len({r['resource_plot'] for r in game['material_retention'] if r['quarter']==q})
        choices=[r for r in river_choices if r['quarter']==q]
        values['river_available']=sum(r['river_available'] for r in choices)
        values['river_chosen_when_available']=sum(r['river_available'] and r['river_chosen'] for r in choices)
        values['mixed_river_options']=sum(r['mixed_river_options'] for r in choices)
        values['river_chosen_when_mixed']=sum(r['mixed_river_options'] and r['river_chosen'] for r in choices)
        values['base_river_available']=sum(r['base_river_available'] for r in choices)
        values['base_river_chosen_when_available']=sum(r['base_river_available'] and r['base_river_chosen'] for r in choices)
        endpoints=[r for r in proxy if r['quarter']==q]
        values['river_endpoint']=sum(r['river'] for r in endpoints)
        values['bonus_endpoint']=sum(r['bonus_copies']>0 for r in endpoints)
        values['only_unmapped_bonus_endpoint']=sum(r['bonus_copies']>0 and r['mapped_bonus_copies']==0 for r in endpoints)
        values['proxy_without_owned_base_endpoint']=sum(r['proxy_without_owned_base'] for r in endpoints)
    game['river_choices']=river_choices;game['endpoint_bonus_proxy']=proxy
    game['improved_plots_per_city']=game['owned_improved_plots']/game['totals']['cities']
    game['improved_plots_per_100_population']=100*game['owned_improved_plots']/game['population']

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('trial','baseline','previous','placement','resource-catalog','output'):
        p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--turn',type=int,default=200)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    sources={'Baseline':a.baseline,'V1 modifiers':a.previous,'Native bonus/river':a.placement,'RH Builder values':a.trial}
    catalog=read(a.resource_catalog);games={};censuses={}
    initial_control=read(a.baseline/'game-01/turn-001.json')['players']
    keys=('id','leader','civ','techs','civics')
    for label,root in sources.items():
        folder=root/'game-01';snapshot=read(folder/f'turn-{a.turn:03d}.json')
        assert snapshot['turn']==a.turn and not snapshot['errors'],label
        assert not any(read(folder/'map-comparison.json')['differences'].values()),label
        initial=read(folder/'turn-001.json')['players']
        assert [{k:p[k] for k in keys} for p in initial]==[{k:p[k] for k in keys} for p in initial_control],label
        previous=[]
        for path in sorted(folder.glob('turn-*.json')):
            if int(path.stem[-3:])>a.turn:continue
            row=read(path);assert not row['errors'] and row['events'][:len(previous)]==previous,label
            assert all(event['turn']<=a.turn for event in row['events']),label
            previous=row['events']
        g=summarize(folder,a.turn);extra(folder,g,catalog,a.turn)
        majors={p['id'] for p in initial};g['improvement_events']=sum(e['event']=='improvement' and e['owner'] in majors for e in snapshot['events'])
        g['per_player']=[]
        for player in snapshot['players']:
            pid=player['id'];cities=[c for c in snapshot['cities'] if c['player']==pid]
            pop=sum(c['population'] for c in cities);n=sum(x['owner']==pid and bool(x.get('improvement')) and not x['pillaged'] for x in snapshot['plots'])
            g['per_player'].append({'player':pid,'leader':player['leader'],'cities':len(cities),'population':pop,'improved_plots':n,'improved_per_city':n/len(cities) if cities else None,'improved_per_100_population':100*n/pop if pop else None})
        games[label]=g
        censuses[label]=[]
        for turn in (50,100,150,200):
            if turn>a.turn:continue
            d=read(folder/f'turn-{turn:03d}.json');count=len(d['cities']);pop=sum(c['population'] for c in d['cities']);n=sum(x['owner'] in majors and bool(x.get('improvement')) and not x['pillaged'] for x in d['plots'])
            censuses[label].append({'turn':turn,'cities':count,'population':pop,'improved_plots':n,'improved_per_city':n/count,'improved_per_100_population':100*n/pop})
    builders=[]
    for turn in (1,50,100,150,200):
        if turn>a.turn:continue
        d=read(a.trial/f'builders-{turn:03d}.json');assert not d['errors'] and d['turn']==turn
        majors={p['player'] for p in d['players']};events=[e for e in d['events'] if e['player'] in majors];counts=Counter(e['event'] for e in events)
        builders.append({'turn':turn,'alive':sum(p['count'] for p in d['players']),'charges':sum(p['charges'] for p in d['players']),'additions':counts['builder_added'],'trained':counts['builder_training_completed'],'purchased':counts['builder_purchased'] if d.get('unit_purchase_subtype') is not None else None,'operation_starts':counts['builder_operation_started']})
    result={'endpoint_turn':a.turn,'trial_complete_at_250':False,'runs':games,'builder_telemetry':builders,'censuses':censuses,'controls':'Same initial map, leaders, starting research and checkpoint turn; zero observer errors and event-prefix checks passed.'}
    (a.output/'comparison.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    for key in ('details','base_placement_choices','improvement_comparison','improvement_timing','material_retention','service_opportunities','timeline','river_choices','endpoint_bonus_proxy','per_player'):
        output_csv(a.output/(key+'.csv'),[{'run':label,**row} for label,g in games.items() for row in g[key]])
    output_csv(a.output/'builder-telemetry.csv',builders)
    lines=[f'# CSC Builder tuning — matched turn-{a.turn} comparison','',f'All four runs evaluated at the beginning of turn {a.turn}. The new run was interrupted later when the user reports Shadow died. This is a valid partial checkpoint comparison; its turn-250 test remains incomplete. Same map, leaders and starting research; CSC with standard AI, Online/Prince/vanilla Standard, TAR/RH disabled.','']
    heading='| Metric | Baseline | V1 modifiers | Native bonus/river | RH Builder values |'
    rule='|---|---:|---:|---:|---:|'
    lines += [heading,rule]
    metrics=[('Cities',lambda g:g['totals']['cities']),('Population',lambda g:g['population']),('Owned unpillaged improved plots',lambda g:g['owned_improved_plots']),('Improved plots per city',lambda g:round(g['improved_plots_per_city'],2)),('Improved plots per 100 population',lambda g:round(g['improved_plots_per_100_population'],1)),('Recorded improvement additions',lambda g:g['improvement_events'])]
    for title,get in metrics:lines.append('| '+title+' | '+' | '.join(str(get(g)) for g in games.values())+' |')
    qm=[('Completed Quarters','completed',None),('Chose mapped Base when available','base_chosen_when_available','base_available'),('Endpoint mapped Base access','base','completed'),('Adjacent owned Base plots improved','base_plots_improved','base_plots'),('Adjacent owned Specialty plots improved','spec_plots_improved','spec_plots'),('Covered supporting material plots','supporting_plots_under_districts','supporting_plots_total'),('Base improvement median wait among completed follow-ups','base_improvement_median_wait',None),('Later sales chose Quarter when available','later_sales_chosen','later_sales_options')]
    for q in ('BAKERS','TAILORS'):
        lines+=['',f'## {q.title()}','',heading,rule]
        for title,n,d in qm:
            values=[fraction(g['quarters'][q].get(n,0),g['quarters'][q].get(d,0)) if d else str(g['quarters'][q].get(n)) for g in games.values()]
            lines.append('| '+title+' | '+' | '.join(values)+' |')
        lines.append('| Stage 2 / 3 / 4 buildings | '+' | '.join(' / '.join(str(g['quarters'][q].get('stage'+str(i),0)) for i in (2,3,4)) for g in games.values())+' |')
    lines+=['','## Service source cities','',heading,rule]
    for prop in sorted(set().union(*(g['service_source_cities'] for g in games.values()))):
        lines.append('| '+prop+' | '+' | '.join(str(g['service_source_cities'].get(prop,0)) for g in games.values())+' |')
    lines+=['','## Improvement density over time','', '| Turn | Baseline | V1 modifiers | Native bonus/river | RH Builder values |',rule]
    for i,turn in enumerate((50,100,150,200)):
        if turn>a.turn:continue
        lines.append('| '+str(turn)+' | '+' | '.join(f"{censuses[label][i]['improved_per_city']:.2f}" for label in games)+' |')
    lines+=['','Values are owned unpillaged improved plots per city.','', '## Builder telemetry — new run only','', '| Turn | Alive | Charges remaining | Added to map | Trained | Purchased |', '|---|---:|---:|---:|---:|---:|---:|']
    for row in builders:lines.append('| '+' | '.join(str(row[k]) for k in ('turn','alive','charges','additions','trained','purchased'))+' |')
    lines+=['','## Interpretation limits','', '- One matched seed with diverging later wars, expansion and research. Matching the time horizon does not isolate causal effects.','- Both improvement valuation and Builder production priority changed together. Historical runs lack Builder production/remaining-charge telemetry; production totals cannot be compared directly.','- Added-to-map events can include captures/grants. Training and purchase event totals are reported separately; operation starts are not completed work.','- Improved plots count all owned unpillaged improvements, including non-Builder improvements. Recorded improvement additions may include rebuilding/captures and are not distinct Builder charges.','- Quarter improvement fractions concern owned mapped resource plots next to completed Quarters, deduplicated within each industry. Opportunities are owned native plot-legal alternatives; affordability is not proven.','- Service source counts are city/Service combinations and need not represent distinct cities.','- No post-200 state is inferred from the archived data; autosaves232/233/234 remain preserved for possible later use.']
    (a.output/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'endpoint_turn':a.turn,'runs':{label:{'cities':g['totals']['cities'],'population':g['population'],'improved':g['owned_improved_plots'],'per_city':g['improved_plots_per_city'],'per_100_pop':g['improved_plots_per_100_population'],'quarters':g['quarters'],'services':g['service_source_cities']} for label,g in games.items()},'builders':builders},ensure_ascii=False))


if __name__=='__main__':main()
