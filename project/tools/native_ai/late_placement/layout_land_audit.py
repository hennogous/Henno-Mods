"""Match historical city reviews to acquisition opportunities and direct ownership observations."""
import argparse
import gzip
import json
from collections import defaultdict
from pathlib import Path

from paired_layout_results import report


def within(plots, center, radius):
    reached = {center}
    for _ in range(radius):
        reached.update({n for i in reached for n in plots[i]['neighbors']})
    return reached


def audit(folder, centers):
    world = json.loads(gzip.decompress((folder.parent/'opening-map.json.gz').read_bytes()))
    plots = world['plots']
    classes = {r['type']: r['class'] for r in world['resources']}
    wonders = {f['type'] for f in world['features'] if f.get('natural_wonder') in (1, True)}
    locations = {(p, c): (int(i), name) for p, c, i, name in centers}
    cases = [r for r in report(folder)['foundations'] if r['turn'] <= 200 and not r['owned_base']
             and r['review'] and r['review']['sites'] and not r['review']['with_base']]
    # These observations have exact foundation-time ownership. The starting
    # resource map supplies the wider geographic ceiling where no receipt exists.
    seen = defaultdict(dict)
    for line in (folder/'Lua.log').open(encoding='utf8', errors='replace'):
        if 'CSC_QUARTER_WATCH_NEIGHBOR\t' in line:
            vals = line.split('CSC_QUARTER_WATCH_NEIGHBOR\t')[1].strip().split('\t')
            r = dict(v.split('=', 1) for v in vals)
            seen[int(r['turn'])][int(r['neighbor'])] = (int(r['owner']), r['resource'], int(r['district']))
    results = []
    for case in cases:
        p, c = case['player'], case['city']
        key = case['district'].split('_')[2]
        base = {r['type'] for r in world['material_tags'] if r['tag'] == 'CLASS_CSC_'+key+'_BASE'}
        actual = case['plot']
        receipt = seen[case['turn']]
        adjacent = [n for n in plots[actual]['neighbors'] if n in receipt and
                    receipt[n][0] == -1 and receipt[n][1] in base and receipt[n][2] == -1]
        row = dict(turn=case['turn'], player=p, city=c, quarter=key, foundation=actual,
                   adjacent_neutral_base=adjacent)
        results.append(row)
        if (p,c) not in locations:
            continue
        center, name = locations[p,c]
        radius = within(plots, center, 3)
        if actual not in radius:
            raise ValueError(f'City mismatch for {actual}')
        row.update(center=center, name=name, supplier_within_purchase_range=sorted(radius.intersection(adjacent)))
        options = []
        for site in sorted(radius-{center}):
            tile = plots[site]
            if tile['water'] or tile['impassable'] or tile.get('feature') in wonders:
                continue
            if tile.get('resource') and classes[tile['resource']] != 'RESOURCECLASS_BONUS':
                continue
            for deposit in tile['neighbors']:
                if plots[deposit].get('resource') not in base or deposit == center:
                    continue
                options.append((site,deposit))
        row['opening_layouts'] = len(options)
        row['opening_base_within_three'] = sorted({d for s,d in options if d in radius})
        row['opening_base_in_fourth_ring'] = sorted({d for s,d in options if d not in radius})
        # Adjacent foundation tiles certify the ownership of BOTH ends only
        # when both were actually observed that turn. Do not backdate the
        # later borders in the city-coordinate save.
        verified = defaultdict(list)
        for s,d in options:
            owner_s = int(p) if s == actual else receipt[s][0] if s in receipt else None
            if s != actual and (s not in receipt or receipt[s][2] >= 0):
                continue
            if d not in receipt or receipt[d][1] not in base or receipt[d][2] >= 0:
                continue
            owner_d = receipt[d][0]
            if owner_s not in (-1,int(p)) or owner_d not in (-1,int(p)):
                continue
            if owner_d == -1 and d not in radius:
                continue
            which = ('both' if owner_s == -1 else 'supplier') if owner_d == -1 else (
                'footprint' if owner_s == -1 else 'owned')
            verified[which].append((s,d))
        row['observed_land_pairs'] = dict(verified)
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('arm',type=Path)
    parser.add_argument('--centers',type=Path)
    args = parser.parse_args()
    centers = json.loads(args.centers.read_text())['cities'] if args.centers else []
    print(json.dumps(audit(args.arm, centers),indent=2))
