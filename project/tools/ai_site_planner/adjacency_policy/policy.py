"""Pure threshold policy; no game IO and no retired heuristic imports."""
from __future__ import annotations
import math
PROFILE='csc-adjacency-policy-v1'
THRESHOLD=4
DELTA_Q8=1048576  # Explicit priority intervention, not economic utility conversion.

def shortlist(snapshot):
    """All eligible >=4 pairs; highest total per city, stable ties by type/plot."""
    if snapshot['turn']>100: raise ValueError('Authorized endpoint is turn100')
    allowed=set(snapshot['originalAI'])
    if allowed & set(snapshot['currentHumans']): raise ValueError('Human in policy scope')
    best={};qualified=[];seen=set()
    for r in snapshot['candidates']:
        key=(r['player'],r['city'],r['district'],r['plot'])
        if key in seen: raise ValueError('Duplicate candidate')
        seen.add(key)
        if r['player'] not in allowed or r['legal'] is not True: raise ValueError('Candidate outside scope')
        if any(not math.isfinite(r[k]) for k in ('production','gold','total')) or abs(r['total']-r['production']-r['gold'])>1e-7: raise ValueError('Invalid adjacency total')
        if r['materialOnSite'] or r['total']<THRESHOLD: continue
        qualified.append(r)
        city=(r['player'],r['city'])
        rank=(-r['total'],r['quarter'],r['plot'])
        if city not in best or rank<best[city][0]: best[city]=(rank,r)
    selected=[best[k][1] for k in sorted(best)]
    if len(selected)>128: raise ValueError('Native policy table capacity exceeded')
    entries=[dict(player=r['player'],city=r['city'],district=r['district'],plot=r['plot'],delta=DELTA_Q8) for r in selected]
    return dict(threshold=THRESHOLD,qualified=qualified,selected=selected,entries=entries,
                incentive_meaning='Strong district proposal priority; not a yield or profit estimate')
