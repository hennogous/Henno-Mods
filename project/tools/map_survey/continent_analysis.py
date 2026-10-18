"""Continent-aware material census for paired native luxury-count experiments."""
import argparse
from collections import Counter
import json
from pathlib import Path
from statistics import mean
from analyze import analyze_map, read, truth, write_csv

FILTERS = ('land', 'common_clearable', 'harvest_aware')


def continent_census(data, definitions):
    plots = {p['index']: p for p in data['plots']}
    resources = {r['type']: r for r in data['resources']}
    features = {f['type']: f for f in data['features']}
    harvests = {r['resource'] for r in data['harvests']}
    names = {c['index']: c for c in data.get('continents', [])}
    ids = sorted({p['continent'] for p in plots.values() if not p['water'] and p.get('continent', -1) >= 0})

    def matches(p, r):
        return p.get('resource') in r.get('resources', []) or (r.get('hills') and p['hills']) or p.get('feature') in r.get('features', [])

    def eligible(p, harvesting=False):
        f = p.get('feature'); r = p.get('resource')
        return not p.get('district') and (not f or truth(features[f].get('removable')) or f in ('FEATURE_FLOODPLAINS', 'FEATURE_FLOODPLAINS_PLAINS', 'FEATURE_FLOODPLAINS_GRASSLAND')) and (not r or resources[r]['class'] == 'RESOURCECLASS_BONUS' or (harvesting and r in harvests))

    result = []
    # -1 is an explicit whole-map aggregate, including water-based source tiles.
    for cid in [-1] + ids:
        region = [p for p in plots.values() if cid == -1 or p.get('continent') == cid]
        land = [p for p in region if not p['water']]
        luxury_counts = Counter(p['resource'] for p in land if p.get('resource') and resources[p['resource']]['class'] == 'RESOURCECLASS_LUXURY')
        info = names.get(cid, {})
        entry = {'id': cid, 'name': 'Whole map' if cid == -1 else info.get('name') or info.get('type') or f'Continent {cid}',
                 'type': info.get('type'), 'land_tiles': len(land), 'passable_land_tiles': sum(not p['impassable'] for p in land),
                 'land_luxury_types': len(luxury_counts), 'land_luxury_tiles': sum(luxury_counts.values()),
                 'luxury_counts': dict(sorted(luxury_counts.items())), 'quarters': []}
        for q, rules in definitions.items():
            # Sources across a continent boundary can still support a candidate.
            base = {i for i, p in plots.items() if matches(p, rules['base'])}
            spec = {i for i, p in plots.items() if matches(p, rules['spec'])}
            counters = Counter()
            candidates = {f'{mask}_{suffix}': set() for mask in FILTERS for suffix in ('base', 'base_only', 'both', 'both_distinct')}
            for p in land:
                if p['impassable']: continue
                adjacent = set(p['neighbors']); b = adjacent & base; s = adjacent & spec
                for mask, allowed in zip(FILTERS, (True, eligible(p), eligible(p, True))):
                    if not allowed: continue
                    counters[mask + '_base'] += bool(b)
                    counters[mask + '_base_only'] += bool(b) and not bool(s)
                    counters[mask + '_both'] += bool(b) and bool(s)
                    counters[mask + '_both_distinct'] += bool(b) and bool(s) and any(a != c for a in b for c in s)
                    for suffix, supported in (('base', bool(b)), ('base_only', bool(b) and not bool(s)), ('both', bool(b) and bool(s)), ('both_distinct', bool(b) and bool(s) and any(a != c for a in b for c in s))):
                        if supported: candidates[mask + '_' + suffix].add(p['index'])
            row = {'quarter': q, 'base_source_tiles': sum(p['index'] in base for p in region), 'spec_source_tiles': sum(p['index'] in spec for p in region)}
            row.update({f'{mask}_{suffix}': counters[f'{mask}_{suffix}'] for mask in FILTERS for suffix in ('base', 'base_only', 'both', 'both_distinct')})
            for key, indices in candidates.items():
                remaining = set(indices); clusters = 0
                while remaining:
                    clusters += 1; pending = [remaining.pop()]
                    while pending:
                        near = set(plots[pending.pop()]['neighbors']) & remaining
                        remaining -= near; pending.extend(near)
                row[key + '_clusters'] = clusters
            entry['quarters'].append(row)
        result.append(entry)
    return result


def analyze_study(folder):
    definitions = read(folder / 'materials.json')
    maps = []; opportunities = []; flat = []; inventories = []
    for path in sorted(folder.glob('luxuries-*/map-*/complete.json')):
        if 'luxury_types_per_continent' not in read(path.parent / 'settings.json'):
            continue  # Export complete; controller still returning to menu/verifying.
        rows, _, summary = analyze_map(path.parent, definitions)
        data = read(path.parent / 'map.json'); settings = read(path.parent / 'settings.json')
        census = continent_census(data, summary['resolved_definitions'])
        whole = census[0]['quarters']
        for row in rows:
            extended = next(r for r in whole if r['quarter'] == row['quarter'])
            assert all(row[k] == extended[k] for k in ('land_both', 'common_clearable_both', 'harvest_aware_both'))
            row.update(extended)
        summary['continents'] = census
        summary['luxury_types_per_continent'] = settings['luxury_types_per_continent']
        for c in census:
            for q in c['quarters']:
                flat.append({'group': summary['group'], 'map': summary['map'], 'continent': c['id'], 'name': c['name'], **q})
            inventories.append({'group': summary['group'], 'map': summary['map'], **{k: v for k, v in c.items() if k not in ('quarters', 'luxury_counts')}, 'luxuries': ';'.join(c['luxury_counts'])})
        maps.append(summary); opportunities.extend(rows)
    comparisons = []
    for i in range(1, 6):
        original = folder / 'luxuries-4' / f'map-{i:02d}' / 'map.json'
        if not original.exists(): continue
        base = read(original)['plots']
        for k in (5, 6):
            other = folder / f'luxuries-{k}' / f'map-{i:02d}' / 'map.json'
            if not other.exists(): continue
            paired = read(other)['plots']
            comparisons.append({'map': i, 'group': f'luxuries-{k}', 'plots': len(base), **{f'same_{key}': sum(p.get(key) == q.get(key) for p, q in zip(base, paired)) for key in ('terrain', 'feature', 'continent', 'resource')}})
    result = {'maps': maps, 'opportunities': opportunities, 'paired_terrain_comparisons': comparisons}
    (folder / 'analysis.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    write_csv(folder / 'continent-opportunities.csv', flat)
    write_csv(folder / 'continent-inventory.csv', inventories)
    write_csv(folder / 'paired-map-comparison.csv', comparisons)
    print(f'Analyzed {len(maps)} maps, {len(flat)} Quarter-region combinations')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    analyze_study(parser.parse_args().output)
