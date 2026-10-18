"""Analyze the paired vanilla/TAR Standard baseline, including partial batches."""
import argparse
from collections import Counter
import json
from pathlib import Path
from analyze import analyze,output_csv,strategy_profiles

def base_opportunities(folder,game):
    """Separate useful Base access from Specialty-only alternatives."""
    final=json.loads((folder/'turn-250.json').read_text(encoding='utf-8'))
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

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output
    games=[analyze(p.parent,250) for p in sorted(out.glob('game-*/complete.json'))]
    for game in games:
        game['group']=game['settings']['group'];game['paired_map']=game['settings']['paired_map']
        game['base_placement_choices']=base_opportunities(out/game['game'],game)
    result={'completed_games':len(games),'endpoint_turn':250,'games':games,'groups':{}}
    for group in ('vanilla-standard','tar-standard'):
        selected=[g for g in games if g['group']==group]
        result['groups'][group]={'games':len(selected),'totals':dict(sum((Counter(g['totals']) for g in selected),Counter())),
            'quarters':{q:dict(sum((Counter(g['quarters'][q]) for g in selected),Counter())) for q in ('BAKERS','TAILORS')},
            'services':dict(sum((Counter(g['service_source_cities']) for g in selected),Counter())),
            'hidden_service_buildings':dict(sum((Counter(g['hidden_service_buildings']) for g in selected),Counter()))}
    (out/'analysis.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    permap=[]
    for g in games:
        for q,v in g['quarters'].items():
            permap.append({'group':g['group'],'map':g['paired_map'],'game':g['game'],'quarter':q,**v})
    output_csv(out/'per-map-quarter-stats.csv',permap)
    for key in ('details','choices','base_placement_choices','improvement_timing','customer_choices','service_opportunities','building_opportunities','improvement_comparison','material_retention','timeline'):
        output_csv(out/(key+'.csv'),[{'group':g['group'],'paired_map':g['paired_map'],'game':g['game'],**v} for g in games for v in g[key]])
    output_csv(out/'strategy_profiles.csv',[{'group':g['group'],'paired_map':g['paired_map'],**r} for g in games for r in strategy_profiles(out/g['game'],g)])
    text=['# CSC AI baseline: paired Standard resource games','',
        f'{len(games)}/10 completed games at the beginning of turn 250. Online speed, Prince, Small map size (74×46) using Continents.lua, six majors and nine city states. Five fixed seed/leader pairs are repeated with TAR disabled and enabled. Both groups use vanilla Standard (2), CSC v3 material assistance, animal resources enabled, unused modded resource cleanup enabled, M&C disabled, standard AI and ordinary victory conditions. No AI tuning or plot manipulation is applied by the observer.','',
        'The five vanilla starting worlds must reproduce the earlier Standard captures tile-for-tile. TAR uses the same seeds and leaders; its resource distribution and resulting starts may differ. These groups compare the mod’s Standard setup, rather than its separate Truly Abundant resource preset. TAR also changes resource placement eligibility and harvesting rules; its group includes those rules throughout gameplay.','',
        '| Setup | Games | Surviving major cities | Completed Bakers | Bakers Base / Both | Completed Tailors | Tailors Base / Both |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for name,g in result['groups'].items():
        b=g['quarters']['BAKERS'];t=g['quarters']['TAILORS']
        text.append(f'| {name} | {g["games"]} | {g["totals"].get("cities",0)} | {b.get("completed",0)} | {b.get("base",0)} / {b.get("both",0)} | {t.get("completed",0)} | {t.get("base",0)} / {t.get("both",0)} |')
    text+=['','Base includes sites with both classes; Both is its subset. These final-state counts require same-owner, revealed materials. They can differ from initial geographic possibilities and placement-time conditions.','',
        '| Setup | Quarter | Placements with Both available | Chose Both | Placements with Base available | Chose Base | Non-City-Center sales adjacency at endpoint |',
        '|---|---|---:|---:|---:|---:|---:|']
    for name,g in result['groups'].items():
        for q,v in g['quarters'].items():text.append(f'| {name} | {q.title()} | {v.get("both_available",0)} | {v.get("both_chosen_when_available",0)} | {v.get("base_available",0)} | {v.get("base_chosen_when_available",0)} | {v.get("non_center_sales",0)} |')
    text+=['','Candidate comparisons cover already owned tiles that pass native plot placement checks, scanned at most one turn before the placement. They do not check production affordability or future purchases. Later capture, border changes, pillage and deposits replaced by districts can change the endpoint. Repeated capture-related district events are excluded from choice counts. A Quarter can remain useful through goods sales without adjacent materials; these comparisons identify material access rather than proving which site was best after all city-planning tradeoffs.','',
        '| Setup | Quarter | Stage 2 / 3 / 4 buildings | Improved adjacent material plots |',
        '|---|---|---:|---:|']
    for name,g in result['groups'].items():
        for q,v in g['quarters'].items():
            rows=[r for gg in games if gg['group']==name for r in gg['improvement_comparison'] if r['quarter']==q and r['adjacent_to_quarter']]
            text.append(f'| {name} | {q.title()} | {v.get("stage2",0)} / {v.get("stage3",0)} / {v.get("stage4",0)} | {sum(r["improved"] for r in rows)} / {len(rows)} |')
    text+=['','## Active Service supply stages','', '| Setup | Property | Source cities |','|---|---|---:|']
    for name,g in result['groups'].items():
        for key,value in sorted(g['services'].items()):text.append(f'| {name} | `{key}` | {value} |')
    text+=['','Supply-stage flags, recipient hidden Service buildings and gate eligibility are retained separately in analysis.json and CSVs. Their counts are not interchangeable. Services and production choices should be assessed against research, source buildings, improved materials and relevant customer venues.','',
        '## Per-map endpoint','', '| Setup | Map | Cities | Bakers: complete / Base / Both | Tailors: complete / Base / Both |','|---|---:|---:|---:|---:|']
    for g in games:
        b=g['quarters']['BAKERS'];t=g['quarters']['TAILORS']
        text.append(f'| {g["group"]} | {g["paired_map"]} | {g["totals"]["cities"]} | {b.get("completed",0)} / {b.get("base",0)} / {b.get("both",0)} | {t.get("completed",0)} / {t.get("base",0)} / {t.get("both",0)} |')
    text+=['','The baseline is observational and small. It reveals choices and missed available opportunities, not the internal AI score or causal understanding of CSC adjacency. Initial and final saves, 25-turn snapshots, full event history, installed/source hashes, map comparisons, exact commands and native logs retain evidence for subsequent tuning.','',
        'Observer v3 enumerates all six native neighbour directions explicitly, including map boundaries, and freezes 25-turn snapshots in memory during continuous autoplay. Previous v1 used sparse adjacency arrays, so historical boundary-site counts are not directly interchangeable. The interrupted turn-50 checkpoint-controller trial is preserved separately and excluded from all results.']
    text+=['','Final-save preparation can release playback queued when control returns at 250. Benchmark snapshots retain the same first-major-activation timing across games. A separate save-state census records any automatic turn-start processing that finishes before serialization. Game 6 had one capital grow 10→11 after disaster playback was closed, without a turn advance; its Quarter, plot, research, Service and event data were unchanged.']
    (out/'report.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    print('Analyzed',len(games),'completed games')

if __name__=='__main__':main()
