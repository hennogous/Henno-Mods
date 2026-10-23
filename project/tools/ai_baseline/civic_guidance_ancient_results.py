"""Read-only per-game reports; safe while another game is being played."""
import argparse
import csv
import json
import sqlite3
from pathlib import Path
from civic_modifier_material_audit import read
from civic_guidance_long_results import checkpoint
from civic_guidance_ancient_audit import TARGETS


def native_events(p):
    events=[]
    for row in csv.reader((p/'native-logs/AI_Victories.csv').read_text().splitlines()):
        row=[x.strip() for x in row]
        if len(row)>=4 and row[2].startswith('STRATEGY_CSC_TEST_LONG_'):
            events.append({'turn':int(row[0]),'player':int(row[1]),'plan':int(row[2].rsplit('_',1)[1]),'status':row[3]})
    return events


def results(p,historical=None):
    assert read(p/'post-run-audit.json')['passed']
    settings=read(p/'game-01/settings.json');obs=read(p/'observations.json')
    checkpoints={str(t):checkpoint(p,t) for t in (200,225,250)}
    for t in (200,250):
        for row in read(p/f'builders-{t:03d}.json')['players']:
            if row['player'] not in range(1,6):continue
            q=checkpoints[str(t)]['per_player'][str(row['player'])]
            q.update(builders=row['count'],charges=row['charges'],builders_per_city=row['count']/q['cities'] if q['cities'] else None)
    events=native_events(p);target_rows=[];reentries=[]
    for pid in range(1,6):
        for plan,civic in enumerate(TARGETS,1):
            states=[x for x in obs['native']['transitions'] if x['player']==pid and x['plan']==plan]
            selections=[x['turn'] for x in obs['history'] if x['player']==pid and x['civic']==civic]
            completions=[x['turn'] for x in obs['completions'] if x['player']==pid and x['civic']==civic]
            adoptions=[x['turn'] for x in events if x['player']==pid and x['plan']==plan and x['status']=='Following']
            target_rows.append({'player':pid,'civic':civic,'first_eligible':next((x['turn'] for x in states if x['eligible']),None),
                'native_following':adoptions,'first_selected':min(selections) if selections else None,
                'completed':min(completions) if completions else None})
            for i,state in enumerate(states):
                stopped=[x['turn'] for x in events if x['player']==pid and x['plan']==plan and x['status']=='Stopped' and x['turn']<state['turn']]
                if not state['eligible'] or not stopped:continue
                end=next((x['turn'] for x in states[i+1:] if not x['eligible']),250)
                returns=[t for t in adoptions if state['turn']<=t<end]
                reentries.append({'player':pid,'civic':civic,'stopped':max(stopped),'eligible_again':state['turn'],
                    'eligible_until':end,'following_again':returns,'stop_to_readoption':returns[0]-max(stopped) if returns else None,
                    'readiness_to_readoption':returns[0]-state['turn'] if returns else None})
    snapshot=read(p/'game-01/turn-250.json');db=sqlite3.connect(p/'native-gameplay.sqlite')
    eras=dict(db.execute('SELECT EraType,ChronologyIndex FROM Eras'))
    tech=dict(db.execute('SELECT TechnologyType,EraType FROM Technologies'));civic=dict(db.execute('SELECT CivicType,EraType FROM Civics'))
    for player in snapshot['players']:
        if player['id'] not in range(1,6):continue
        q=checkpoints['250']['per_player'][str(player['id'])]
        q['highest_tech_era']=max((tech[x] for x in player['techs']),key=eras.get)
        q['highest_civic_era']=max((civic[x] for x in player['civics']),key=eras.get)
    naval_favorites=list(db.execute("SELECT ListType,Favored,Value FROM AiFavoredItems WHERE Item='CIVIC_NAVAL_TRADITION'"));db.close()
    active_cities=sum(any(value>0 for value in c['properties'].values()) for c in snapshot['cities'] if c['player'] in range(1,6))
    result={'run':read(p/'complete.json')['run'],'scope':'Players1-5 only; player0 explicitly excluded and native adoption checked',
            'settings':settings,'checkpoints':checkpoints,'targets':target_rows,'native_strategy_events':events,
            'reentry_episodes':reentries,'active_service_cities':active_cities,'direct_naval_favorite_rows':naval_favorites,
            'target_completion_counts':{c:sum(x['civic']==c for x in obs['completions']) for c in TARGETS}}
    if (p/'supply-signal-review.json').exists():result['supply_signal_review']=read(p/'supply-signal-review.json')
    if historical:
        hv=read(historical/'source-version/version.json');v=read(p/'source-version/version.json')
        hs=read(historical/'game-01/settings.json');a=read(p/'game-01/initial-map.json');b=read(historical/'game-01/initial-map.json')
        result['historical_comparison']={'path':str(historical),'code_version':hv['code_version'],'settings':hs,
            'checkpoints':{str(t):checkpoint(historical,t) for t in (200,225,250)},
            'installed_files_differ':[rel for rel,h in v['installed_files'].items() if hv['installed_files'].get(rel)!=h],
            'initial_world_field_differences':{k:sum(x.get(k)!=y.get(k) for x,y in zip(a['plots'],b['plots'])) for k in ('terrain','feature','resource','resource_count','continent','owner')},
            'starting_plots_identical':a['starting_plots']==b['starting_plots'],
            'naval_completed_at250':[x['id'] for x in read(historical/'game-01/turn-250.json')['players'] if x['id'] in range(1,6) and 'CIVIC_NAVAL_TRADITION' in x['civics']],
            'causal_control':False,'caveat':'Same recorded map/start positions do not remove policy/adjacency/code/legacy-guidance confounds.'}
    (p/'compact-results.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def report(p,r):
    q=r['checkpoints']['250'];show=lambda x:'—' if x is None else str(x)
    audit=read(p/'post-run-audit.json')
    lines=[f"# Ancient guidance Game {r['run']} — turn250",'',
      f"Audited complete:{audit['observations']}/1,245 uncensored-maximum player-turn observations; {len(audit['defeat_censored_pairs'])} explicit defeat-censored pairs. Map/game seeds {r['settings']['map_seed']}/{r['settings']['game_seed']}; Online/Prince/Small/Continents/Ancient. Statistics cover players1–5. Legacy preferences absent; player0 never adopted guidance; private yields zero; original preferences restored after this run. The next authorized run may now have its own installed overlay active.",'',
      f"Endpoint: **{q['cities']} cities, {q['population']} population, {sum(v['completed'] for v in q['quarters'].values())} completed Quarters, {q['service_total']} active Service source/stage flags across {r['active_service_cities']} cities.**",'',
      '| Player | Cities | Pop | Bakers/Tailors | Services | Naval completed | Builders (charges) | Builders/city | Techs/civics |',
      '|---|---:|---:|---|---:|---:|---|---:|---|']
    for pid,x in q['per_player'].items():
        leader=r['settings']['leaders'][int(pid)].replace('LEADER_','')
        naval=next(t for t in r['targets'] if t['player']==int(pid) and t['civic']=='CIVIC_NAVAL_TRADITION')
        lines.append(f"| {leader} | {x['cities']} | {x['population']} | {x['quarters'].get('BAKERS',0)}/{x['quarters'].get('TAILORS',0)} | {sum(x['services'].values())} | {show(naval['completed'])} | {x['builders']} ({x['charges']}) | {x['builders_per_city']:.2f} | {x['techs']}/{x['civics']} |")
    lines+=['','## Research timing','','Selection means observed progressing civic; it is distinct from eligibility, strategy adoption and natural completion. A dash means not observed. No causal claim from timing alone.','','| Player | Target | First eligible | Native Following | First selected | Completed |','|---|---|---:|---|---:|---:|']
    for row in r['targets']:
        lines.append(f"| {r['settings']['leaders'][row['player']].replace('LEADER_','')} | {row['civic'].replace('CIVIC_','')} | {show(row['first_eligible'])} | {','.join(map(str,row['native_following'])) or '—'} | {show(row['first_selected'])} | {show(row['completed'])} |")
    guided_naval=[x['player'] for x in r['targets'] if x['civic']=='CIVIC_NAVAL_TRADITION' and x['native_following']]
    guided_opera=[x['player'] for x in r['targets'] if x['civic']=='CIVIC_OPERA_BALLET' and x['native_following']]
    lines+=['',f"Direct Naval guidance was adopted by players {guided_naval}; the other Naval completions cannot be claimed as direct targeted-guidance successes. Opera guidance adopters: {guided_opera}. There are no direct/static Naval AiFavoredItems rows: {r['direct_naval_favorite_rows']}."]
    lines+=['','## Checkpoints and Service constraints','','| Turn | Cities | Population | Quarters | Active Service source/stages |','|---|---:|---:|---:|---:|']
    for t,x in r['checkpoints'].items():lines.append(f"| {t} | {x['cities']} | {x['population']} | {sum(a['completed'] for a in x['quarters'].values())} | {x['service_total']} |")
    lines+=['','| Service | Quarters | Civic | Producer | Materials | Improved materials | Venue | Active |','|---|---:|---:|---:|---:|---:|---:|---:|']
    for k,x in q['bottlenecks'].items():lines.append('| '+k+' | '+' | '.join(str(x[n]) for n in ('quarters','civic_unlocked','source_building','owned_materials','improved_materials','nearby_venue','source_activation'))+' |')
    lines+=['','Gate columns are separate marginal counts, not additive failure reasons. Service counts are source/stage flags, not distinct cities or monetary transactions. Source/venue links are retained in compact-results.json.','',
      '## Materials, improvements and Builders','','| Quarter | Completed | With Base | With both classes | No mapped material | Mean correct adj. | Mean unmapped adj. | Adj. mapped plots improved |','|---|---:|---:|---:|---:|---:|---:|---|']
    for name,x in q['quarters'].items():lines.append(f"| {name} | {x['completed']} | {x['base_adjacent']} | {x['both_adjacent']} | {x['zero_owned_materials']} | {x['avg_owned_mapped_resources']:.2f} | {x['avg_owned_unmapped_resources']:.2f} | {x['unique_adjacent_mapped_improved']}/{x['unique_adjacent_mapped_plots']} |")
    improvements=sum(x['improvements'] for x in q['per_player'].values());builders=sum(x['builders'] for x in q['per_player'].values());charges=sum(x['charges'] for x in q['per_player'].values())
    lines+=['',f"Unpillaged improvements {improvements} ({improvements/q['cities']:.2f}/city); surviving Builders {builders}, charges {charges}, pooled {builders/q['cities']:.2f} Builders/city. These are unit censuses, not all Builders produced. Material adjacency is owned and mapped to that industry. Shared plots can contribute to multiple Quarters/industries.",'',
      'Preservation:'+json.dumps(q['preservation'])+'. An improvement observed before a later district is not proof of its state immediately before replacement.','',
      '## Native strategy re-entry','','Readiness and Following are separate observations. Episodes after a prior native Stopped record:', '']
    for row in r['reentry_episodes']:lines.append('- '+json.dumps(row))
    lines+=['','A native re-adoption demonstrates that restart is possible in this run, not universal reliability. Matching stop-to-return delays suggest a reconsideration/cooldown hypothesis; that mechanism is not established by these timestamps alone.','',
      '## Research eras','','Highest unlocked era, not complete mastery of that era:','', '| Player | Technology era | Civic era |','|---|---|---|']
    for pid,x in q['per_player'].items():lines.append(f"| {r['settings']['leaders'][int(pid)].replace('LEADER_','')} | {x['highest_tech_era']} | {x['highest_civic_era']} |")
    if 'historical_comparison' in r:
        h=r['historical_comparison'];old=h['checkpoints']['250']
        lines+=['','## Historical context — not a fresh control','',
          f"Compared with {h['code_version']}: Naval Tradition completed by {len(h['naval_completed_at250'])}/5 previously versus {r['target_completion_counts']['CIVIC_NAVAL_TRADITION']}/5 now; active Services {old['service_total']}→{q['service_total']}; cities {old['cities']}→{q['cities']}; population {old['population']}→{q['population']}.",
          f"Recorded terrain/features/resources/counts/continents/initial ownership differences: {h['initial_world_field_differences']}. Starting plots identical: {h['starting_plots_identical']}. However {len(h['installed_files_differ'])} installed text/code/manifests differ, including policy/adjacency/Quarter definitions and the research treatment. This is a combined, historical comparison, not isolated causal evidence."]
    if 'supply_signal_review' in r:
        supply=r['supply_signal_review']
        lines+=['','## Existing supply-probe warnings','',
            f"Final probe actual turn {supply['actual_probe_turn']}; primary census actual turn {supply['primary_turn']}. Its old formula wrongly stacks improvement80 per Quarter and counts presence40 for incomplete sources. The preserved flagged-sample review is supply-signal-review.json. If the actual turns differ, the primary-state reconstruction is context, not an exact simultaneous validation. One warning can remain an eligibility edge rather than a controller failure; do not rewrite the accepted baseline to fit it. Earlier UI probes can be later than their named primary checkpoint and are not retrospectively declared passed."]
        for x in r['supply_signal_review']['flagged_sample_reviews']:
            if not x['explained']:lines.append('- Unresolved under the broad corrected expectation: '+json.dumps(x)+'. Review source completion, pillage, ownership and improvement compatibility before interpreting this warning. Game1 had a Wheat Farm beside only an unfinished Quarter with actual0, qualifying the assumption about precompletion improvement80. The research gate explicitly requires completed/unpillaged Quarters.')
    lines+=['','Full audit: post-run-audit.json; complete machine-readable metrics: compact-results.json. No candidate deployment or extra games.','']
    (p/'results.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('run',type=Path);parser.add_argument('--historical',type=Path)
    args=parser.parse_args();x=results(args.run,args.historical);report(args.run,x)
    print(json.dumps({'run':x['run'],'target_completions':x['target_completion_counts'],'services':x['checkpoints']['250']['services'],'reentries':x['reentry_episodes']}))
