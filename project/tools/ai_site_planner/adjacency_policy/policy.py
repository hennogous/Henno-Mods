"""Pure adjacency priorities; no game IO or retired heuristic imports."""
from __future__ import annotations
import math
PROFILE='csc-adjacency-policy-v2'
THRESHOLD=4
DELTA_Q8=1048576  # Explicit priority intervention, not economic utility conversion.
PENALTY_PER_POINT_Q8=65536
MAX_PENALTY_Q8=262144
CAPACITY=4096


def penalty(total):
    """Soft signed subtraction: 256 native units per missing adjacency point.

    The scale is an experimental priority, not a price for a yield. Negative
    native results can still win; this deliberately does not impose a ban.
    """
    return -min(MAX_PENALTY_Q8,math.ceil((THRESHOLD-total)*PENALTY_PER_POINT_Q8)) if total<THRESHOLD else 0

def shortlist(snapshot):
    """Promote one best >=4 pair/city; penalize every observed sub-4 pair."""
    if snapshot['turn']>100: raise ValueError('Authorized endpoint is turn100')
    allowed=set(snapshot['originalAI'])
    if allowed & set(snapshot['currentHumans']): raise ValueError('Human in policy scope')
    best={};qualified=[];weak=[];seen=set()
    for r in snapshot['candidates']:
        key=(r['player'],r['city'],r['district'],r['plot'])
        if key in seen: raise ValueError('Duplicate candidate')
        seen.add(key)
        if r['player'] not in allowed or r['legal'] is not True: raise ValueError('Candidate outside scope')
        if any(not math.isfinite(r[k]) for k in ('production','gold','total')) or abs(r['total']-r['production']-r['gold'])>1e-7: raise ValueError('Invalid adjacency total')
        if r['total']<THRESHOLD:
            weak.append(r)
            continue
        if r['materialOnSite']: continue
        qualified.append(r)
        city=(r['player'],r['city'])
        rank=(-r['total'],r['quarter'],r['plot'])
        if city not in best or rank<best[city][0]: best[city]=(rank,r)
    selected=[best[k][1] for k in sorted(best)]
    entries=[dict(player=r['player'],city=r['city'],district=r['district'],plot=r['plot'],delta=DELTA_Q8) for r in selected]
    entries += [dict(player=r['player'],city=r['city'],district=r['district'],plot=r['plot'],delta=penalty(r['total'])) for r in sorted(weak,key=lambda r:(r['player'],r['city'],r['district'],r['plot']))]
    if len(entries)>CAPACITY: raise ValueError('Native policy table capacity exceeded')
    return dict(threshold=THRESHOLD,qualified=qualified,selected=selected,penalized=weak,entries=entries,
                penalty_per_missing_point_Q8=PENALTY_PER_POINT_Q8,maximum_penalty_Q8=MAX_PENALTY_Q8,
                incentive_meaning='Signed district proposal priorities; not a yield or profit estimate; weak sites remain selectable')
