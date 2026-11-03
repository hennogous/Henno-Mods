"""Offline native harvest-job origins; no native control or inferred utility weights."""
import argparse,json,re,sqlite3
from pathlib import Path
from material_decision_intelligence import report as decision_report

def origin(system,boosts):
    match=re.fullmatch(r'Seek (?:Tech|Civic) Boost ((?:TECH|CIVIC)_[A-Z0-9_]+)',system)
    if match:
        target=match[1]
        return dict(kind='boost',native_system=system,target=target,loaded_boost_rows=[b for b in boosts if b.get('TechnologyType')==target or b.get('CivicType')==target])
    return dict(kind='city'if system.startswith('City ')else'other',native_system=system,target=None,loaded_boost_rows=[])

def strategy_at(transitions,player,turn):
    prior=[x for x in transitions if x['player']==player and x['turn']<=turn]
    if not prior:return dict(observed=False,active=None,last_transition=None)
    # Export order preserves multiple transitions within the same native turn.
    last=max(enumerate(prior),key=lambda x:(x[1]['turn'],x[0]))[1]
    return dict(observed=True,active=last['active'],last_transition=last)

def enrich(case,boosts,transitions):
    reservation=case.get('first_matching_reservation')
    if reservation is None:return dict(case=case,origin=None,care_strategy_at_reservation=dict(observed=False,active=None,last_transition=None),missing_reservation=True)
    value=origin(reservation['system'],boosts)
    value['requested_improvement_matches_boost']=any(b.get('ImprovementType')==reservation.get('improvement')for b in value['loaded_boost_rows'])if value['loaded_boost_rows']else None
    return dict(case=case,origin=value,care_strategy_at_reservation=strategy_at(transitions,case['player'],reservation['turn']),missing_reservation=False,decision_utility_weights_observed=False)

def report(root,through):
    root=Path(root);care=json.loads((root/'material-care'/f'turn-{through:03d}.json').read_text(encoding='utf-8-sig'))
    db=sqlite3.connect((root/'native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
    try:boosts=[dict(x)for x in db.execute('SELECT * FROM Boosts')]
    finally:db.close()
    decisions=decision_report(root,through)
    cases=[enrich(c,boosts,care['strategy']['transitions'])for c in decisions['cases']]
    return dict(root=str(root),through=through,confirmed_native_harvest_cases=len(cases),cases=cases,summary=dict(city_jobs=sum(c['origin']is not None and c['origin']['kind']=='city'for c in cases),boost_jobs=sum(c['origin']is not None and c['origin']['kind']=='boost'for c in cases),other_or_unmatched=sum(c['origin']is None or c['origin']['kind']=='other'for c in cases),active_care_strategy_at_first_reservation=sum(c['care_strategy_at_reservation']['active']is True for c in cases)),scope='Confirmed harvests, logged first matching reservations, loaded boost definitions and observed player-strategy state; not hidden job creation time or causality.',limits=['A strategy being active does not establish which values the native job evaluator consumed.','The native TechBoosts HAVE_X_IMPROVEMENTS handler serves many useful improvements as well as destructive Mine/Farm jobs; globally disabling it is not a targeted material fix.','No exact utility weights, actual Service payments, complete material retention or independent-world effects inferred.'])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('--through',required=True,type=int);p.add_argument('--output',required=True,type=Path);a=p.parse_args();v=report(a.root,a.through);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8');print(json.dumps(v['summary']))
