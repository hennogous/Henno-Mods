"""Offline coverage of one or two signed native adjacency counts on saved maps."""
import argparse
from collections import Counter
import gzip
from itertools import combinations
import json
from pathlib import Path

import numpy as np


def coverage(world):
    plots = {p['index']: p for p in world['plots']}
    bonus = {r['type'] for r in world['resources'] if r['class'] == 'RESOURCECLASS_BONUS'}
    removable = {f['type'] for f in world['features'] if f.get('removable')}
    clear = {i for i,p in plots.items() if not (p['water'] or p['impassable'] or p.get('district'))
             and (not p.get('resource') or p['resource'] in bonus)
             and (not p.get('feature') or p['feature'] in removable or p['feature'].startswith('FEATURE_FLOODPLAINS'))}
    counts = {}
    for i in sorted(clear):
        neighbors = [plots[j] for j in plots[i]['neighbors']]
        counts[i] = Counter(p[k] for p in neighbors for k in ('terrain','feature') if p.get(k))
    columns = sorted(set().union(*(set(c) for c in counts.values())))
    features = np.array([[counts[i][k] for k in columns] for i in sorted(clear)], dtype=np.int8)
    row = {p:i for i,p in enumerate(sorted(clear))}
    families = {}
    # Scores stack linearly. Include both signs and use each identity once.
    # Count a neighborhood only if its best real supplier outranks EVERY
    # material-free site on this component, including ties at the top.
    for family, cols in [('terrain',[i for i,k in enumerate(columns) if k.startswith('TERRAIN_')]),
                         ('terrain_feature',list(range(len(columns))))]:
        scores = [features[:,i]*sign for i in cols for sign in (1,-1)]
        single_count = len(scores)
        for i,j in combinations(cols,2):
            scores.extend(features[:,i]*a + features[:,j]*b for a,b in ((1,1),(1,-1),(-1,1),(-1,-1)))
        families[family] = np.stack(scores,axis=1), single_count
    result = {}
    for quarter in ('BAKERS','TAILORS'):
        base = {r['type'] for r in world['material_tags'] if r['tag']==f'CLASS_CSC_{quarter}_BASE'}
        deposits = {i for i,p in plots.items() if p.get('resource') in base and not p.get('district')}
        totals = Counter()
        for center in sorted(clear):
            if center % 3:
                continue
            reach = {center}
            for _ in range(3):
                reach.update({j for i in reach for j in plots[i]['neighbors']})
            sites = (reach & clear)-{center}
            good = {i for i in sites if (set(plots[i]['neighbors']) & deposits)-{center}}
            bad = sites-good
            if not good or not bad:
                continue
            totals['mixed_neighborhoods'] += 1
            for family,(scores,split) in families.items():
                margin = scores[[row[i] for i in good]].max(axis=0)-scores[[row[i] for i in bad]].max(axis=0)
                totals[family+'_one'] += int(max(margin[:split])>0)
                totals[family+'_up_to_two'] += int(margin.max()>0)
                totals[family+'_margin_two'] += int(margin.max()>=2)
        result[quarter] = totals
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('maps',type=Path,nargs='+')
    args=parser.parse_args()
    for path in args.maps:
        with gzip.open(path,'rt',encoding='utf-8') as stream:
            print(path.parent.name, json.dumps(coverage(json.load(stream))))
