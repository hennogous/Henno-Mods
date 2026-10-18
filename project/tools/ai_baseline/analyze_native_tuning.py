"""Compare the native bonus/river trial, v1 and the matched untuned baseline.

No game connection. Reuse the established real-material analyses unchanged;
add river decisions and endpoint bonus-proxy matches from the archived worlds.
"""
import argparse
import json
from pathlib import Path
from analyze import read, output_csv, fraction
from analyze_tuning import summarize


def extra(folder, game, resources):
    initial=read(folder/'turn-001.json'); final=read(folder/'turn-250.json')
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
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('trial','baseline','previous','resource-catalog'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    sources={'Baseline':args.baseline,'V1 modifiers':args.previous,'Native bonus/river':args.trial}
    catalog=read(args.resource_catalog)
    games={}
    for label,root in sources.items():
        folder=root/'game-01';assert read(folder/'complete.json')['turn']==250
        game=summarize(folder);extra(folder,game,catalog);games[label]=game
    baseline=games['Baseline']
    initial_keys=('id','leader','civ','techs','civics')
    initial_control=read(args.baseline/'game-01/turn-001.json')['players']
    for label,game in games.items():
        assert game['leaders']==baseline['leaders'],label
        assert not game['observer_errors'],label
        assert not any(read(sources[label]/'game-01/map-comparison.json')['differences'].values()),label
        initial=read(sources[label]/'game-01/turn-001.json')['players']
        assert [{k:p[k] for k in initial_keys} for p in initial]==[{k:p[k] for k in initial_keys} for p in initial_control],label
    probe=read(args.trial/'placement-probe.json')
    isolated=[r for r in probe.get('rows',[]) if r['legal'] and r['adjacent_districts']==0 and r.get('native_value') is not None]
    positive=[r for r in isolated if r['bonus_river_expected']>0]
    probe_summary={k:probe.get(k) for k in ('turn','status','isolated_checks','isolated_matches','errors')}
    probe_summary.update(isolated_nonzero_checks=len(positive),isolated_nonzero_matches=sum(abs(r['native_value']-r['bonus_river_expected'])<0.001 for r in positive),
        isolated_bonus_checks=sum(r['bonus']>0 for r in isolated),isolated_river_checks=sum(r['river'] for r in isolated))
    nonhuman={p['id'] for p in initial_control if not p['human']}
    restricted={label:{q:{key:sum(int(row[key]) for row in game['base_placement_choices'] if row['quarter']==q and row['player'] in nonhuman)
        for key in ('base_available','base_chosen_when_available','base_sales_available','base_sales_chosen_when_available')}
        for q in ('BAKERS','TAILORS')} for label,game in games.items()}
    result={'runs':games,'material_choices_nonhuman':restricted,'native_probe':probe_summary,
        'limitations':['One matched starting world; later expansion, wars and material retention diverge.',
            'Combined treatment: bonus, river and improvement weights are not isolated.',
            'Placement alternatives are owned native-plot-legal scans at most one turn old; affordability and future purchases are not proven.',
            'Bonus proxy statistics describe the endpoint, not resource state at the time of placement.',
            'Marker experiment is a modified 20-turn fixture and is excluded from the natural-game comparison.',
            'Primary tables retain all six autoplay majors. V1 conditional material modifiers excluded human-flagged player 0; native signals apply during its autoplay too. Nonhuman-only choices are retained separately.']}
    (args.trial/'comparison.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    for key in ('details','base_placement_choices','customer_choices','improvement_comparison','improvement_timing','material_retention','service_opportunities','building_opportunities','timeline','river_choices','endpoint_bonus_proxy'):
        output_csv(args.trial/(key+'.csv'),[{'run':label,**row} for label,game in games.items() for row in game[key]])
    lines=['# CSC native bonus-resource/river trial — matched seed 1','',
        'Online/Prince/Standard, Small Continents, turn 250. Same starting world and leaders; unchanged read-only observer v3. CSC with standard AI, TAR/RH disabled.','',
        '| Metric | Baseline | V1 modifiers | Native bonus/river |','|---|---:|---:|---:|']
    for title,getter in [('Cities',lambda g:g['totals']['cities']),('Population',lambda g:g['population']),
                         ('Owned unpillaged improved plots',lambda g:g['owned_improved_plots']),
                         ('Improved plots per city',lambda g:round(g['improved_plots_per_city'],2)),
                         ('Improved plots per 100 population',lambda g:round(g['improved_plots_per_100_population'],1))]:
        lines.append('| '+title+' | '+' | '.join(str(getter(g)) for g in games.values())+' |')
    metrics=[('Completed','completed',None),('Chose actual Base when available','base_chosen_when_available','base_available'),
        ('Chose actual Base + sales when available','base_sales_chosen_when_available','base_sales_available'),
        ('Chose river when available','river_chosen_when_available','river_available'),
        ('Chose river with mixed alternatives','river_chosen_when_mixed','mixed_river_options'),
        ('Chose actual Base + river when available','base_river_chosen_when_available','base_river_available'),
        ('Quarter chose sales when available','quarter_sales_chosen','quarter_sales_options'),
        ('Later sales chose Quarter when available','later_sales_chosen','later_sales_options'),
        ('Endpoint actual Base','base','completed'),('Endpoint river','river_endpoint','completed'),
        ('Endpoint non-City-Center sales','non_center_sales','completed'),
        ('Adjacent owned Base plots improved','base_plots_improved','base_plots'),
        ('Supporting material plots later covered by districts','supporting_plots_under_districts',None),
        ('Covered supporting plots / all original supporting plots','supporting_plots_under_districts','supporting_plots_total'),
        ('Endpoint bonus adjacency','bonus_endpoint','completed'),
        ('Endpoint bonus adjacency, all bonus neighbours unmapped','only_unmapped_bonus_endpoint','bonus_endpoint'),
        ('Endpoint bonus adjacency without actual owned Base','proxy_without_owned_base_endpoint','bonus_endpoint')]
    for quarter in ('BAKERS','TAILORS'):
        lines+=['',f'## {quarter.title()}','', '| Metric | Baseline | V1 modifiers | Native bonus/river |','|---|---:|---:|---:|']
        for title,n,d in metrics:
            values=[fraction(g['quarters'][quarter].get(n,0),g['quarters'][quarter].get(d,0)) if d else str(g['quarters'][quarter].get(n,0)) for g in games.values()]
            lines.append('| '+title+' | '+' | '.join(values)+' |')
        lines.append('| Stage 2 / 3 / 4 buildings | '+' | '.join(' / '.join(str(g['quarters'][quarter].get('stage'+str(i),0)) for i in (2,3,4)) for g in games.values())+' |')
    lines+=['','## Native Service source cities','', '| Property | Baseline | V1 modifiers | Native bonus/river |','|---|---:|---:|---:|']
    for prop in sorted(set().union(*(g['service_source_cities'] for g in games.values()))):
        lines.append('| '+prop+' | '+' | '.join(str(g['service_source_cities'].get(prop,0)) for g in games.values())+' |')
    lines+=['','## Actual Base choices excluding human-flagged player 0','', '| Quarter | Baseline | V1 modifiers | Native bonus/river |','|---|---:|---:|---:|']
    for quarter in ('BAKERS','TAILORS'):
        lines.append('| '+quarter.title()+' | '+' | '.join(fraction(counts[quarter]['base_chosen_when_available'],counts[quarter]['base_available']) for counts in restricted.values())+' |')
    lines+=['','## Native probe','',json.dumps(result['native_probe']), '', '## Limits','',*['- '+x for x in result['limitations']]]
    (args.trial/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({label:{'cities':g['totals']['cities'],'improved_plots':g['owned_improved_plots'],'quarters':g['quarters'],'services':g['service_source_cities']} for label,g in games.items()}))


if __name__=='__main__':main()
