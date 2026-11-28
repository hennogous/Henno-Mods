"""Join each Quarter foundation to the city's preceding opportunity assessment."""
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
from full_game_results import quarter_rows


def foundations(arm):
    world=json.loads(gzip.decompress((arm.parent/'opening-map.json.gz').read_bytes()))
    tags=defaultdict(set)
    for row in world['material_tags']:
        name=row['tag']
        if name.startswith('CLASS_CSC_') and name.endswith('_BASE'):
            tags['DISTRICT_CSC_'+name[10:-5]+'_QUARTER'].add(row['type'])
    indices, reviews, sites, neighbors = {}, {}, {}, defaultdict(set)
    counts=defaultdict(Counter)
    seats={str(p['id']) for p in world['players'] if p['id']!=0}
    with (arm/'Lua.log').open(encoding='utf-8',errors='replace') as stream:
        for line in stream:
            if 'CSC_NO_BASE_REVIEW\t' in line:
                turn,pid,city,kind,reason,changed=line.split('CSC_NO_BASE_REVIEW\t')[1].strip().split('\t')[:6]
                reviews[pid,city,kind]=reason,int(turn)
                counts['reviews'][reason]+=1
            if 'CSC_QUARTER_WATCH_' not in line:
                continue
            event,_,tail=line.split('CSC_QUARTER_WATCH_',1)[1].partition('\t')
            row=dict(v.split('=',1) for v in tail.strip().split('\t') if '=' in v)
            if event=='DISTRICT_INDEX':
                indices[row['index']]=row['districtType']
            elif row.get('event')=='foundation':
                at=(row['turn'],row['plot'])
                if event=='SITE' and row['player'] in seats:
                    key=row['player'],row['city'],row['district']
                    reason,stamp=reviews.get(key,('unreviewed',None))
                    sites[at]=(key,reason,stamp,int(row['base']))
                if event=='NEIGHBOR' and row['district']=='-1':
                    neighbors[at].add(row['resource'])
    # Earlier control logs predate the district-index header. The physical
    # census still identifies the exact Quarter on the same foundation plot.
    if any(key[2] not in indices for key,_,_,_ in sites.values()):
        known={str(q['plot']):q['profile'] for f in arm.glob('full-census-*.json') for q in quarter_rows(f)}
        for (_,plot),(key,_,_,_) in sites.items():
            if plot in known:
                indices.setdefault(key[2],'DISTRICT_CSC_'+known[plot]+'_QUARTER')
    for at, (key,reason,stamp,owned) in sites.items():
        kind=indices[key[2]]
        if kind not in tags:
            raise ValueError('Missing material mapping for '+kind)
        counts[kind]['founded']+=1
        counts[kind]['owned_base']+=bool(owned)
        counts[kind]['any_base']+=bool(neighbors[at]&tags[kind])
        counts[kind]['after_'+reason]+=1
        if not neighbors[at]&tags[kind]:
            counts[kind]['weak_after_'+reason]+=1
    return dict(counts)


if __name__=='__main__':
    import sys
    for arg in sys.argv[1:]:
        arm=Path(arg)
        print(arm.name,json.dumps(foundations(arm),indent=2))
