from material_checkpoint_logs import reconstruct_checkpoint
"""Archived native boost records; preserves labels without inventing boost counts."""
import sqlite3
from pathlib import Path
from log_intelligence import reconstruct,records

def boost_records(text,through,first=16):
    return [dict(turn=t,player=p,target=row[2],native_progress_label=row[3],raw=raw)for t,p,row,raw in records(text,first,through,set(range(1,6)))if len(row)>=4]

def events_for_job(case,events):
    value=case.get('origin');reservation=case.get('case',{}).get('first_matching_reservation')
    if not value or value['kind']!='boost'or not reservation:return None
    return [e for e in events if e['player']==case['case']['player']and e['target']==value['target']and e['turn']>=reservation['turn']]

def report(root,through):
    root=Path(root);text,coverage=reconstruct_checkpoint(root,'Game_Boosts.csv',through)
    if coverage['gaps']or coverage['conflicting_segments']:raise AssertionError('Incomplete/conflicting native boost log')
    events=boost_records(text,through);db=sqlite3.connect((root/'native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True)
    try:targets={tech or civic for tech,civic in db.execute("SELECT TechnologyType,CivicType FROM Boosts WHERE BoostClass='BOOST_TRIGGER_HAVE_X_IMPROVEMENTS'")}
    finally:db.close()
    return dict(through=through,first_observed_turn=16,left_censored_before_source=True,events=events,improvement_count_boost_records=[e for e in events if e['target']in targets],native_progress_label_interpreted=False,scope='Recorded boost events16..endpoint; not number of Mines built, full initial boost state, or attribution to one Builder job.',coverage=coverage)
