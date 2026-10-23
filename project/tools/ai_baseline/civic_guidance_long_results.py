"""Compact AI-only postprocessing of the completed long guidance pair."""
import argparse
import collections
import csv
import json
import sqlite3
from pathlib import Path
from analyze import analyze, distance, SERVICE_GATES, STAGES
from civic_modifier_material_audit import read, scores

PIDS = range(1,6)
TARGETS = ['CIVIC_FEUDALISM','CIVIC_MEDIEVAL_FAIRES','CIVIC_URBANIZATION',
           'CIVIC_NAVAL_TRADITION','CIVIC_DIVINE_RIGHT','CIVIC_OPERA_BALLET']


def sequence(obs,pid):
    out=[]
    for x in obs['history']:
        if x['player']==pid and (not out or out[-1]['civic']!=x['civic']):out.append(x)
    return out


def checkpoint(p,t):
    s=read(p/f'game-01/turn-{t:03d}.json');summary=analyze(p/'game-01',t)
    cities=[x for x in s['cities'] if x['player'] in PIDS]
    details=[x for x in summary['details'] if x['player'] in PIDS]
    op=[x for x in summary['service_opportunities'] if x['player'] in PIDS]
    materials=[x for x in summary['improvement_comparison'] if x['player'] in PIDS]
    quarter_rows={};per_player={};links=collections.Counter();active_links=collections.Counter()
    plots={x['index']:x for x in s['plots']}
    for q in ('BAKERS','TAILORS'):
        ds=[(c,d) for c in cities for d in c['districts'] if d.get('quarter')==q and d['complete']]
        mapped=incorrect=0
        for c,d in ds:
            for plot in s['plots']:
                if plot.get('owner')==c['player'] and plot.get('resource') and distance(d,plot,s['width'])==1:
                    if plot['resource'] in s['quarters'][q]['base'] or plot['resource'] in s['quarters'][q]['spec']:mapped+=1
                    else:incorrect+=1
            source_buildings={b['type'] for b in c['buildings'] if not b['pillaged']}
            for stage,civic,venues,prop in SERVICE_GATES[q]:
                if not source_buildings.intersection(STAGES[q][stage-2]) or d['pillaged']:continue
                for recipient in cities:
                    if recipient['player']!=c['player']:continue
                    for b in recipient['buildings']:
                        if b['type'] in venues and not b['pillaged'] and b['plot'] in plots and distance(d,plots[b['plot']],s['width'])==1:
                            label=q+str(stage)+' -> '+b['type']
                            links[label]+=1
                            if (c.get('properties') or {}).get(prop,0)>0:active_links[label]+=1
        d=[x for x in details if x['quarter']==q]
        adj=[x for x in materials if x['quarter']==q and x['adjacent_to_quarter']]
        quarter_rows[q]={'completed':len(d),'base_adjacent':sum(x['base']>0 for x in d),
                         'spec_adjacent':sum(x['spec']>0 for x in d),'both_adjacent':sum(x['base']>0 and x['spec']>0 for x in d),
                         'zero_owned_materials':sum(x['base']==0 and x['spec']==0 for x in d),
                         'owned_mapped_adjacency_incidences':mapped,'owned_unmapped_adjacency_incidences':incorrect,
                         'avg_owned_mapped_resources':mapped/len(d) if d else 0,
                         'avg_owned_unmapped_resources':incorrect/len(d) if d else 0,
                         'unique_adjacent_mapped_plots':len(adj),'unique_adjacent_mapped_improved':sum(x['improved'] for x in adj)}
    for pid in PIDS:
        cs=[x for x in cities if x['player']==pid];ds=[x for x in details if x['player']==pid]
        native=next(x for x in s['players'] if x['id']==pid)
        playerplots=[x for x in s['plots'] if x.get('owner')==pid]
        per_player[str(pid)]={'cities':len(cs),'population':sum(x['population'] for x in cs),
            'quarters':dict(collections.Counter(x['quarter'] for x in ds)),
            'improvements':sum(bool(x.get('improvement')) and not x['pillaged'] for x in playerplots),
            'improvements_per_city':sum(bool(x.get('improvement')) and not x['pillaged'] for x in playerplots)/len(cs) if cs else None,
            'techs':len(native['techs']),'civics':len(native['civics']),
            'services':dict(collections.Counter(x['quarter']+str(x['stage']) for x in op if x['player']==pid and x['source_activation']))}
    services=dict(collections.Counter(x['quarter']+str(x['stage']) for x in op if x['source_activation']))
    bottlenecks={q+str(stage):{'quarters':sum(x['quarter']==q and x['stage']==stage for x in op),
                 **{key:sum(x[key] for x in op if x['quarter']==q and x['stage']==stage)
                    for key in ('civic_unlocked','source_building','owned_materials','improved_materials','nearby_venue','source_activation')}}
                 for q in ('BAKERS','TAILORS') for stage in (2,3,4)}
    retention=[x for x in summary['material_retention'] if x['player'] in PIDS]
    loss=[x for x in retention if not x['resource_retained']]
    # This is improvement state WHEN the Quarter was placed, not necessarily
    # immediately before a later district removed that adjacent resource.
    placement={}
    for e in s['events']:
        if e['event']=='district' and e.get('quarter'):
            placement.setdefault((e['player'],e['plot']),e)
    formerly_improved=[]
    improved_before_replacement=[]
    for x in loss:
        old=placement.get((x['player'],x['quarter_plot']),{})
        m=next((m for m in old.get('site',{}).get('materials',[]) if m['plot']==x['resource_plot']),{})
        if m.get('improvement'):formerly_improved.append(x)
        later_districts=[e for e in s['events'] if e['event']=='district' and e['plot']==x['resource_plot'] and e['turn']>old.get('turn',250)]
        if later_districts:
            first=min(e['turn'] for e in later_districts)
            improvements=[e for e in s['events'] if e['event']=='improvement' and e['plot']==x['resource_plot'] and e['owner']==x['player'] and e.get('resource')==x['initial_resource'] and old.get('turn',71)<=e['turn']<first]
            if m.get('improvement') or improvements:improved_before_replacement.append(x)
    completed=[(c,d) for c in cities for d in c['districts'] if d.get('quarter') and d['complete']]
    return {'cities':len(cities),'population':sum(c['population'] for c in cities),
            'quarters':quarter_rows,'services':services,'service_total':sum(services.values()),
            'per_player':per_player,'bottlenecks':bottlenecks,
            'source_venue_links':dict(links),'source_active_venue_links':dict(active_links),
            'preservation':{'adjacent_mapped_at_placement_incidences':len(retention),
                'resource_lost':len(loss),'lost_to_final_district':sum(bool(x['final_district']) for x in loss),
                'lost_while_previously_improved_at_quarter_placement':len(formerly_improved),
                'unique_lost_plots_with_observed_improvement_before_later_district':len({x['resource_plot'] for x in improved_before_replacement}),
                'unique_lost_plots':len({x['resource_plot'] for x in loss})},
            'active_property_but_gate_summary_false':sum(x['source_activation'] and not all(x[k] for k in ('civic_unlocked','source_building','owned_materials','improved_materials','nearby_venue')) for x in op),
            'all_gate_summary_true_but_property_inactive':sum(not x['source_activation'] and all(x[k] for k in ('civic_unlocked','source_building','owned_materials','improved_materials','nearby_venue')) for x in op)}


def results(root):
    assert read(root/'post-run-audit.json')['passed']
    out={'scope':'Reported metrics cover players1-5 only. Autoplay player0 is excluded from metrics but unexpectedly activated two guidance strategies; it was not an untreated observer.',
         'arms':{}}
    comparison=read(root/'comparison.json');observations={};measured={}
    for arm in ('off','on'):
        p=root/arm;obs=read(p/'observations.json');observations[arm]=obs
        db=sqlite3.connect(p/'native-gameplay.sqlite')
        era_order={row[0]:row[1] for row in db.execute('SELECT EraType,ChronologyIndex FROM Eras')}
        tech_eras=dict(db.execute('SELECT TechnologyType,EraType FROM Technologies'))
        civic_eras=dict(db.execute('SELECT CivicType,EraType FROM Civics'))
        measured[arm]=scores(p/'native-logs/AI_GovtPolicies.csv')
        checkpoints={str(t):checkpoint(p,t) for t in (200,225,250)}
        endpoint=read(p/'game-01/turn-250.json')
        for player in endpoint['players']:
            if player['id'] not in PIDS:continue
            pr=checkpoints['250']['per_player'][str(player['id'])]
            pr['highest_tech_era']=max((tech_eras[x] for x in player['techs']),key=lambda e:era_order[e])
            pr['highest_civic_era']=max((civic_eras[x] for x in player['civics']),key=lambda e:era_order[e])
        db.close()
        for t in (200,250):
            builders=read(p/f'builders-{t}.json')
            for b in builders['players']:
                if b['player'] not in PIDS:continue
                x=checkpoints[str(t)]['per_player'][str(b['player'])]
                x.update(builders=b['count'],charges=b['charges'],builders_per_city=b['count']/x['cities'] if x['cities'] else None)
        strategy_events=[]
        for row in csv.reader((p/'native-logs/AI_Victories.csv').read_text().splitlines()):
            row=[x.strip() for x in row]
            if len(row)>=4 and row[2].startswith('STRATEGY_CSC_TEST_LONG_'):
                strategy_events.append({'turn':int(row[0]),'player':int(row[1]),'plan':int(row[2].rsplit('_',1)[1]),'status':row[3]})
        reeligible=[]
        for x in obs['native']['transitions']:
            prior=[e for e in strategy_events if e['player']==x['player'] and e['plan']==x['plan'] and e['status']=='Stopped' and e['turn']<x['turn']]
            if x['eligible'] and prior:
                following=[e['turn'] for e in strategy_events if e['player']==x['player'] and e['plan']==x['plan'] and e['status']=='Following' and e['turn']>=x['turn']]
                reeligible.append({**x,'last_stopped':max(e['turn'] for e in prior),'subsequent_following':following})
        supply=[]
        for t in (100,150,200,250):
            probe=read(p/f'supply-signal-{t}.json');snap=read(p/f'game-01/turn-{t}.json')
            plotmap={x['index']:x for x in snap['plots']};mismatches=[];raw=0
            for x in probe['plots']:
                # Review the legacy warnings only. Snapshot city censuses omit
                # city states and can differ from UI timing on other plots.
                if x['actual']==x['expected']:continue
                raw+=1
                resource=plotmap[x['plot']];near=[]
                for city in snap['cities']:
                    if city['player']!=x['player']:continue
                    for d in city['districts']:
                        q=d.get('quarter')
                        if q and distance(d,resource,snap['width'])==1 and (resource.get('resource') in snap['quarters'][q]['base'] or resource.get('resource') in snap['quarters'][q]['spec']):near.append(d)
                # Quarter presence is lost on incomplete/pillaged sources.
                # Improvement attachment is once per industry, and its existing
                # district-count predicate does not exclude pillaged sources.
                expected=40*sum(d['complete'] and not d['pillaged'] for d in near)
                if x['improved']:expected+=80*len({d['quarter'] for d in near})
                if x['actual']!=expected:mismatches.append({**x,'corrected_expected':expected})
            supply.append({'turn':t,'sampled_plots':len(probe['plots']),'legacy_formula_mismatches':raw,'unexplained_legacy_warnings_after_rule_review':mismatches})
        out['arms'][arm]={'checkpoints':checkpoints,'research':comparison['arms'][arm]['research_per_player'],
                         'strategy_events':strategy_events,'reeligible_after_stop':reeligible,
                         'autoplay0_strategy_events':[x for x in strategy_events if x['player']==0],
                         'supply_signal_audit':supply,
                         'natural_target_completions':{c:sum(e['civic']==c for e in obs['completions']) for c in TARGETS}}
    out['first_path_divergence']={}
    for pid in PIDS:
        seq={a:sequence(o,pid) for a,o in observations.items()}
        divergence=next((i for i,(x,y) in enumerate(zip(seq['off'],seq['on'])) if x['civic']!=y['civic']),None)
        out['first_path_divergence'][str(pid)]={'common_prefix_choices':divergence if divergence is not None else min(map(len,seq.values())),
            'off':seq['off'][divergence] if divergence is not None else None,
            'on':seq['on'][divergence] if divergence is not None else None}
    initial={k:v for k,v in measured['off'].items() if k[0]==71}
    out['initial_score_records_equal']=all(measured['on'].get(k)==v for k,v in initial.items())
    out['initial_score_record_count']=len(initial)
    out['score_deltas75']={str(pid):{c:round(measured['on'][(75,pid,c)]-measured['off'][(75,pid,c)],3)
                           for c in TARGETS if all((75,pid,c) in measured[a] for a in ('off','on'))} for pid in PIDS}
    (root/'compact-results.json').write_text(json.dumps(out,indent=2)+'\n')
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();r=results(a.root)
    print(json.dumps({'initial_equal':r['initial_score_records_equal'],
        'target_completions':{a:x['natural_target_completions'] for a,x in r['arms'].items()},
        'reeligible_after_stop':{a:x['reeligible_after_stop'] for a,x in r['arms'].items()},
        'first_path_divergence':r['first_path_divergence']}))
