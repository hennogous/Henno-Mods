"""Offline upper bound for steering owned Quarter sites with three weighted terrain clues."""
import argparse
from collections import defaultdict
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path

import numpy as np

from floor_coverage import decode


@lru_cache(maxsize=32)
def patterns(size):
    # A row describes up to three city-local native terrain adjacencies.
    # Magnitudes are private yield units per neighboring hex. Keep this
    # exhaustive search outside Civ; it measures what the inputs can express.
    rows=[]
    for width in range(1,min(3,size)+1):
        for indices in combinations(range(size),width):
            for amounts in product((-6,-3,3,6),repeat=width):
                if max(amounts)<0:
                    continue
                row=[0]*size
                for i,w in zip(indices,amounts):
                    row[i]=w
                rows.append(row)
    return np.array(rows,dtype=np.int16)


def measure(sites, keys, results, context):
    weights=patterns(len(keys))
    if not weights.size:
        return
    counts=np.array([[s.counts.get(k,0) for k in keys] for s in sites],dtype=np.int16)
    ranked=np.array([s.rank for s in sites])
    unknown=np.array([s.unknown for s in sites])
    ring=np.array([sum(s.counts.values())+s.unknown for s in sites])
    known=weights @ counts.T
    # Each unrevealed neighbor can provide only one terrain. Zero includes
    # unselected terrains and makes both extrema conservative.
    high=known+weights.max(axis=1).clip(min=0)[:,None]*unknown
    low=known+weights.min(axis=1).clip(max=0)[:,None]*unknown
    recorded=defaultdict(set)
    for floor in (0,1):
        ceiling=high-floor*ring
        # Bound the disruption to unrelated sites. Check every recorded weak
        # footprint and keep even the worst-case deduction within 12 units.
        safe=(ceiling[:,ranked==0].max(axis=1)<=0) & ((low-floor*ring).min(axis=1)>=-12)
        safe &= ceiling.max(axis=1)<=12
        for i,site in enumerate(sites):
            if not site.rank:
                continue
            gain=ceiling[:,i]
            for cutoff in (6,12):
                ok=safe & (gain>=cutoff)
                if np.any(ok):
                    recorded[f'any_{cutoff}'].add(site.plot)
                    if site.rank==ranked.max():
                        recorded[f'best_{cutoff}'].add(site.plot)
                        rivals=np.delete(ceiling, i, axis=1)
                        if np.any(ok & (gain>rivals.max(axis=1))):
                            recorded[f'unique_best_{cutoff}'].add(site.plot)
    for k,plots in recorded.items():
        result=results[k]
        result['reviews']+=1
        result['cities'].add(context[:2])
        result['targets'].update((context[2],p) for p in plots)


def main(path):
    results=defaultdict(lambda:defaultdict(lambda:dict(reviews=0,cities=set(),targets=set())))
    eligible=0
    ambiguous=0
    for line in path.open(encoding='utf-8-sig',errors='replace'):
        _,sep,fields=line.partition('CSC_LAYOUT_GEOMETRY\t')
        if not sep or len(line.rstrip('\r\n'))>=2047:
            continue
        turn,player,city,quarter,current,rows=fields.rstrip('\r\n').split('\t')
        sites=decode(rows)
        if not any(s.rank for s in sites) or all(s.rank for s in sites):
            continue
        eligible+=1
        keys=sorted({key for s in sites for key in s.counts})
        # Count hard collisions even before imposing an additive scoring rule:
        # every top-ranked target shares its complete terrain counts with an
        # observed weak site. Ignore incomplete rivals for this lower bound.
        weak_signatures={tuple(s.counts.get(k,0) for k in keys) for s in sites if not s.rank and not s.unknown}
        top=max(s.rank for s in sites)
        ambiguous+=all(tuple(s.counts.get(k,0) for k in keys) in weak_signatures
                       for s in sites if s.rank==top)
        land=[k for k in keys if not k.endswith(('_MOUNTAIN','_COAST','_OCEAN'))]
        for name,terms in [('land',land),('all',keys)]:
            measure(sites,terms,results[name],(player,city,quarter))
    print('Eligible mixed reviews:',eligible,'; all top sites have a fully observed weak terrain twin:',ambiguous)
    for name,metrics in results.items():
        print(name, {k:(v['reviews'],len(v['cities']),len(v['targets'])) for k,v in sorted(metrics.items())})


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log',type=Path)
    main(parser.parse_args().log)
