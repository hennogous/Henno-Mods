"""Measure native landscape targets for a future approximate terrain generator.

Each of the five paired landscapes counts once. This does not generate terrain.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
from statistics import mean


def profile(data):
    plots = data['plots']; land = {p['index'] for p in plots if not p['water']}
    remaining = set(land); components = []
    while remaining:
        pending = [remaining.pop()]; size = 0
        while pending:
            i = pending.pop(); size += 1
            near = set(plots[i]['neighbors']) & remaining; remaining -= near; pending.extend(near)
        components.append(size)
    continents = Counter(p['continent'] for p in plots if not p['water'])
    values = {'land_fraction': len(land) / len(plots), 'land_tiles': len(land),
              'hills_land_fraction': sum(p['hills'] for p in plots if not p['water']) / len(land),
              'mountains_land_fraction': sum('MOUNTAIN' in p['terrain'] for p in plots if not p['water']) / len(land),
              'river_land_fraction': sum(p['river'] for p in plots if not p['water']) / len(land),
              'wooded_land_fraction': sum(p.get('feature') in ('FEATURE_FOREST','FEATURE_JUNGLE') for p in plots if not p['water']) / len(land),
              'lake_tiles': sum(p['lake'] for p in plots), 'landmass_components': len(components),
              'continent_count': len(continents), 'largest_landmass_fraction': max(components) / len(land)}
    return {'metrics': values, 'terrain_counts': dict(Counter(p['terrain'] for p in plots)),
            'feature_counts': dict(Counter(p.get('feature') or 'NONE' for p in plots)),
            'named_continent_land_sizes': sorted(continents.values(), reverse=True),
            'connected_landmass_sizes': sorted(components, reverse=True),
            'latitude_bands': [{'band': band, 'tiles': sum(p['y'] * 6 // data['height'] == band for p in plots),
                                'land': sum(p['index'] in land and p['y'] * 6 // data['height'] == band for p in plots),
                                'terrain_counts': dict(Counter(p['terrain'] for p in plots if p['y'] * 6 // data['height'] == band))} for band in range(6)]}


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--study', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); cases = []
    for folder in sorted((a.study / 'luxuries-4').glob('map-*')):
        if not (folder / 'complete.json').exists(): continue
        data = json.loads((folder / 'map.json').read_text()); settings = json.loads((folder / 'settings.json').read_text())
        cases.append({'map': settings['map_number'], 'map_seed': settings['map_seed'], **profile(data)})
    assert len(cases) == 5
    keys = cases[0]['metrics']
    result = {'landscapes': 5, 'scope': 'Small Continents-script sample; descriptive calibration targets, not universal map-generation rules.',
              'summary': {k: {'minimum': min(c['metrics'][k] for c in cases), 'mean': mean(c['metrics'][k] for c in cases), 'maximum': max(c['metrics'][k] for c in cases)} for k in keys}, 'cases': cases}
    a.output.parent.mkdir(parents=True, exist_ok=True); a.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result['summary']))


if __name__ == '__main__': main()
