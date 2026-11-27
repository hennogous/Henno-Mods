"""Survey city-local terrain cues against the actual Base deposits in captured maps."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path


def survey(data):
    plots = {p['index']: p for p in data['plots']}
    removable = {f['type'] for f in data['features'] if f.get('removable')}
    bonus = {r['type'] for r in data['resources'] if r['class'] == 'RESOURCECLASS_BONUS'}
    terrains = {r['type'] for r in data['terrains'] if not r.get('water') and not r.get('impassable')}
    clear = {i for i, p in plots.items() if not (p['water'] or p['impassable'] or p.get('district'))
             and (not p.get('resource') or p['resource'] in bonus)
             and (not p.get('feature') or p['feature'] in removable or p['feature'].startswith('FEATURE_FLOODPLAINS'))}
    terrain_counts = {i: Counter(plots[j].get('terrain') for j in plots[i]['neighbors']) for i in clear}
    # These are possible radius-three neighborhoods before ownership. Exclude
    # the center itself from Quarter sites and from future material suppliers.
    neighborhoods = {}
    for center in sorted(clear):
        if center % 3:
            continue
        reached = {center}
        for _ in range(3):
            reached.update({j for i in reached for j in plots[i]['neighbors']})
        neighborhoods[center] = sorted((reached & clear) - {center})

    result = {}
    for quarter in ('BAKERS', 'TAILORS'):
        bases = {r['type'] for r in data['material_tags'] if r['tag'] == f'CLASS_CSC_{quarter}_BASE'}
        source_plots = {i for i, p in plots.items() if p.get('resource') in bases and not p.get('district')}
        neighbors = {i: source_plots.intersection(plots[i]['neighbors']) for i in clear}
        stats = Counter()
        for center, sites in neighborhoods.items():
            good = {i for i in sites if neighbors[i] - {center}}
            if not good:
                continue
            stats['with_base_opportunity'] += 1
            if len(good) == len(sites):
                stats['every_site_already_good'] += 1
                continue
            choices = {plots[n]['terrain'] for i in good for n in neighbors[i] - {center}} & terrains
            thresholds = []
            for terrain in choices:
                best_bad = max(terrain_counts[i][terrain] for i in sites if i not in good)
                best_good = max(terrain_counts[i][terrain] for i in good)
                if best_good > best_bad:
                    # Even a linear effect puts these good sites ahead on its
                    # own component. An actual zero below the cutoff would
                    # require the native effect to round at that threshold.
                    thresholds.append(best_bad + 1)
            if thresholds:
                stats['highest_terrain_count_only_on_good_sites'] += 1
                stats[f'minimum_count_{min(thresholds)}'] += 1
        result[quarter] = stats
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('map', type=Path, help='Map-lab catalogue or one controller opening-map.json.gz')
    parser.add_argument('--group', default='vanilla-abundant')
    args = parser.parse_args()
    if args.map.suffix == '.gz':
        with gzip.open(args.map, 'rt', encoding='utf-8') as stream:
            maps = [json.load(stream)]
    else:
        catalogue = json.loads(args.map.read_bytes())
        maps = [m['data'] for m in catalogue['maps'] if m['group'] == args.group]
    if not maps:
        parser.error('No maps matched')
    totals = {'BAKERS': Counter(), 'TAILORS': Counter()}
    for data in maps:
        for quarter, counts in survey(data).items():
            totals[quarter].update(counts)
    print(json.dumps(dict(maps=len(maps), quarters=totals), indent=2))
