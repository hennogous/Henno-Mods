"""Compare preserved turn-200 state with the turn-400 continuation."""
import argparse
from collections import Counter
from pathlib import Path
from analyze import analyze, read, STAGES, SERVICE_GATES, output_csv

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    folders=[f for f in sorted(a.output.glob('game-*')) if (f/'complete.json').exists()]
    endpoints={t:[analyze(f,t) for f in folders] for t in (200,400)}
    census=[];decisions=[];unlocks=[];building_exposure=[]
    for folder in folders:
        snapshots=[read(path) for path in sorted(folder.glob('turn-*.json'))]
        final=snapshots[-1]
        for s in snapshots:
            for q in STAGES:
                districts=[(c,d) for c in s['cities'] for d in c['districts'] if d.get('quarter')==q and d['complete']]
                census.append({'game':folder.name,'turn':s['turn'],'quarter':q,'cities':len(s['cities']),'completed':len(districts),**{'stage'+str(stage):sum(bool({b['type'] for b in c['buildings'] if not b['pillaged']}.intersection(buildings)) for c,d in districts) for stage,buildings in enumerate(STAGES[q],2)},'service_source_stages':sum(value>0 for c in s['cities'] for key,value in (c.get('properties') or {}).items() if key.startswith('CSC_'+q+'_'))})
        late=next(g for g in endpoints[400] if g['game']==folder.name)
        for name in ('choices','customer_choices'):
            for e in late[name]:decisions.append({'kind':name,'period':'1-199' if e['turn']<200 else '200-399',**e})
        for player in final['players']:
            pid=player['id']
            for q,gates in SERVICE_GATES.items():
                for stage,civic,venues,prop in gates:
                    first=next((s['turn'] for s in snapshots if any(p['id']==pid and civic in p['civics'] for p in s['players'])),None)
                    unlocks.append({'game':folder.name,'player':pid,'leader':player['leader'],'quarter':q,'stage':stage,'civic':civic,'unlocked_at_400':civic in player['civics'],'first_observed_turn':first,'minimum_turns_unlocked':400-first if first is not None else 0})
        # For each endpoint Quarter, find the start of its continuous recorded
        # same-owner, completed and research/prerequisite-ready snapshot run.
        ref=read(a.output/'mechanics-reference.json');defs={b['BuildingType']:b for b in ref['buildings']}
        for c in final['cities']:
            for d in c['districts']:
                if not d.get('quarter') or not d['complete']:continue
                q=d['quarter']
                for stage,buildings in enumerate(STAGES[q],2):
                    first=None
                    for s in reversed(snapshots):
                        owner=next((p for p in s['players'] if p['id']==c['player']),None)
                        city=next((x for x in s['cities'] if x['player']==c['player'] and any(y['plot']==d['plot'] and y['type']==d['type'] and y['complete'] for y in x['districts'])),None)
                        if not owner or not city:break
                        bs={b['type'] for b in city['buildings'] if not b['pillaged']}
                        research=any((not defs[bt]['PrereqTech'] or defs[bt]['PrereqTech'] in owner['techs']) and (not defs[bt]['PrereqCivic'] or defs[bt]['PrereqCivic'] in owner['civics']) for bt in buildings)
                        if not research or (stage>2 and not bs.intersection(STAGES[q][0])):break
                        first=s['turn']
                    built=bool({b['type'] for b in c['buildings'] if not b['pillaged']}.intersection(buildings))
                    building_exposure.append({'game':folder.name,'player':c['player'],'city':c['name'],'plot':d['plot'],'quarter':q,'stage':stage,'built_at_400':built,'continuously_ready_observed_since':first,'minimum_snapshot_window':400-first if first is not None else 0})
    for name,values in [('timeline',census),('decisions_by_period',decisions),('service_civic_exposure',unlocks),('building_exposure',building_exposure)]:output_csv(a.output/(name+'.csv'),values)
    import json
    summary={'endpoint_aggregates':{str(t):{'totals':dict(sum((Counter(g['totals']) for g in gs),Counter())),'quarters':{q:dict(sum((Counter(g['quarters'][q]) for g in gs),Counter())) for q in STAGES},'service_source_cities':dict(sum((Counter(g['service_source_cities']) for g in gs),Counter())),'hidden_service_buildings':dict(sum((Counter(g['hidden_service_buildings']) for g in gs),Counter()))} for t,gs in endpoints.items()},'notes':['First research observation bounds the unlock time; it is not the exact unlock turn.','Continuous building readiness is checked at snapshots, not every turn, and omits affordability and other restrictions.','Placement periods use event turn <200 versus >=200; captures are deduplicated by the main analyzer.']}
    (a.output/'longitudinal.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
