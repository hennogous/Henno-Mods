"""Preview a sparse, continental CSC resource helper on immutable native maps.

This does not run Civ or install a mod. Eligibility uses the same SQL-rule
interpretation checked against native samples by calibrate.py/world.lua.
"""
import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import json
from pathlib import Path
import random
import sqlite3
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'map_survey'))
from continent_analysis import continent_census
from analyze import write_csv
from build import render

PROBABILITIES = {'TAILORS': 7 / 12, 'STONEMASONS': 6 / 11,
                 'APOTHECARIES': 1 / 6, 'GOLDSMITHS': 3 / 13}
SEED = 20261016


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def stable_seed(*parts):
    return int.from_bytes(hashlib.sha256('|'.join(map(str, parts)).encode()).digest()[:8], 'big')


def matches(p, rule):
    return bool(p.get('resource') in rule.get('resources', []) or
                rule.get('hills') and p['hills'] or p.get('feature') in rule.get('features', []))


class Rules:
    def __init__(self, database):
        with sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True) as db:
            db.row_factory = sqlite3.Row
            self.resources = {r['ResourceType']: dict(r) for r in db.execute('SELECT * FROM Resources')}
            self.features = {r['FeatureType']: dict(r) for r in db.execute('SELECT * FROM Features')}
            self.terrains = {tuple(r) for r in db.execute('SELECT ResourceType,TerrainType FROM Resource_ValidTerrains')}
            self.valid_features = {tuple(r) for r in db.execute('SELECT ResourceType,FeatureType FROM Resource_ValidFeatures')}

    def can_place(self, p, resource, plots):
        r = self.resources[resource]
        if p.get('resource') or p.get('district') or p['impassable'] or p['water']:
            return False
        f = p.get('feature')
        if f and self.features[f]['NaturalWonder']: return False
        if r['NoRiver'] and p['river'] or r['RequiresRiver'] and not p['river']: return False
        if p['lake'] and not r['LakeEligible']: return False
        if f: return (resource, f) in self.valid_features
        if (resource, p['terrain']) not in self.terrains: return False
        if r['AdjacentToLand'] and not any(not plots[i]['water'] for i in p['neighbors']): return False
        return True


class Helper:
    def __init__(self, source, rules, seed=SEED):
        self.source = source
        self.data = copy.deepcopy(source['data'])
        self.plots = self.data['plots']
        self.definitions = source['definitions']
        self.rules = rules
        self.seed = seed
        self.rng = random.Random(stable_seed(seed, source['settings']['map_seed'], 'placement'))
        self.ids = sorted(c['id'] for c in source['continents'] if c['id'] != -1)
        self.regions = {c: [p for p in self.plots if p.get('continent') == c and not p['water']] for c in self.ids}
        self.resource_classes = {r['type']: r['class'] for r in self.data['resources']}
        self.features = {r['type']: r for r in self.data['features']}
        self.local_types = {c: {p.get('resource') for p in ps if p.get('resource')} for c, ps in self.regions.items()}
        self.additions, self.attempts = [], []
        self.palette, self.allocated = {}, Counter()
        self.budget = Counter()
        self.reserved_centers = set()
        # Eligibility is static except for occupancy, which is checked separately.
        mapped = {r for d in self.definitions.values() for k in ('base', 'spec') for r in d[k].get('resources', [])}
        self.available = sorted(r for r in mapped if r in self.resource_classes and r in rules.resources
                                and rules.resources[r]['Frequency'] > 0)
        self.eligible = {r: {p['index'] for p in self.plots if rules.can_place(p, r, self.plots)} for r in self.available}
        self.baseline_sites = self.sites()
        self.base_sites = self.sites(mode='base')
        self.prepare_palettes()

    def clearable(self, p):
        f = self.features.get(p.get('feature'))
        return (not p['water'] and not p['impassable'] and not p.get('district') and
                (not f or f.get('removable') or p.get('feature') in
                 ('FEATURE_FLOODPLAINS', 'FEATURE_FLOODPLAINS_PLAINS', 'FEATURE_FLOODPLAINS_GRASSLAND')) and
                (not p.get('resource') or self.resource_classes[p['resource']] == 'RESOURCECLASS_BONUS'))

    def sites(self, mode='both'):
        result = {}
        for q, d in self.definitions.items():
            base = {p['index'] for p in self.plots if matches(p, d['base'])}
            spec = {p['index'] for p in self.plots if matches(p, d['spec'])}
            for c in self.ids:
                result[c, q] = {p['index'] for p in self.regions[c] if self.clearable(p)
                                and base.intersection(p['neighbors']) and (mode == 'base' or spec.intersection(p['neighbors']))}
        return result

    def weighted(self, values, weights):
        return self.rng.choices(values, weights=weights, k=1)[0]

    def prepare_palettes(self):
        # One soft palette per native named continent. Allocate a preferred
        # feasible type per material class, penalizing reuse across continents.
        order = self.ids.copy(); self.rng.shuffle(order)
        for q in PROBABILITIES:
            for kind in ('base', 'spec'):
                for c in order:
                    choices = [r for r in self.definitions[q][kind].get('resources', [])
                               if r in self.available and any(p['index'] in self.eligible[r] for p in self.regions[c])]
                    if not choices: continue
                    weights = [(4 if r in self.local_types[c] else 2) / (1 + 3 * self.allocated[r]) for r in choices]
                    r = self.weighted(choices, weights)
                    self.palette[c, q, kind] = r
                    self.allocated[r] += 1

    def options(self, c, q, current):
        """Successful single deposits first; bounded pair only if none exist."""
        d = self.definitions[q]
        by_cost = {1: {}, 2: {}}
        protected = {next(iter(v)) for v in current.values() if len(v) == 1} | self.reserved_centers
        for center in self.regions[c]:
            if not self.clearable(center): continue
            near = center['neighbors']
            present = {k: any(matches(self.plots[i], d[k]) for i in near) for k in ('base', 'spec')}
            if all(present.values()): continue
            needs = [k for k in ('base', 'spec') if not present[k]]
            choices = {}
            for kind in needs:
                choices[kind] = [(i, r) for r in d[kind].get('resources', []) if r in self.available
                                 for i in near if self.plots[i].get('continent') == c and i in self.eligible[r]
                                 and not self.plots[i].get('resource') and i not in protected]
            if any(not choices[k] for k in needs): continue
            combos = ((a,) for a in choices[needs[0]]) if len(needs) == 1 else (
                (a, b) for a in choices['base'] for b in choices['spec'] if a[0] != b[0])
            for combo in combos:
                key = tuple(sorted(combo))
                by_cost[len(combo)].setdefault(key, {'deposits': key, 'center': center['index'], 'needs': needs})
        return list(by_cost[1].values()) or list(by_cost[2].values())

    def choose(self, options, c, q, current):
        # Draw resource combinations before locations; widespread habitat does
        # not swamp rarer mapped resources simply by supplying more tiles.
        types = defaultdict(list)
        for option in options:
            if self.budget[c] + len(option['deposits']) > 4 or len(self.additions) + len(option['deposits']) > 10: continue
            # A luxury/strategic addition may consume a previously usable center.
            # Preserve at least one site for every currently covered industry
            # on every continent, including cross-boundary dependencies.
            for i, r in option['deposits']: self.plots[i]['resource'] = r
            after = self.sites_local(option['deposits'], current)
            base_after = self.sites_local(option['deposits'], self.base_sites, mode='base')
            safe = all(not old or after[key] for key, old in current.items()) and all(not old or base_after[key] for key, old in self.base_sites.items())
            for i, _ in option['deposits']: self.plots[i].pop('resource')
            if safe: types[tuple(sorted(r for _, r in option['deposits']))].append(option)
        if not types: return None
        keys = sorted(types)
        def weight(rs):
            w = 1
            for r in rs:
                preferred = any(self.palette.get((c, q, k)) == r for k in ('base', 'spec'))
                elsewhere = sum(1 for a in self.additions if a['resource'] == r and a['continent'] != c)
                w *= (12 if preferred else 4 if r in self.local_types[c] else 1) / (1 + 3 * elsewhere)
            return w
        chosen = self.weighted(keys, [weight(rs) for rs in keys])
        return self.rng.choice(types[chosen])

    def sites_local(self, deposits, before, mode='both'):
        # Only the occupied deposit cells and their neighbours can change.
        affected = {i for i, _ in deposits}
        for i, _ in deposits: affected.update(self.plots[i]['neighbors'])
        after = {key: values - affected for key, values in before.items()}
        for i in affected:
            p = self.plots[i]; c = p.get('continent')
            if c not in self.ids or not self.clearable(p): continue
            for q, d in self.definitions.items():
                if all(any(matches(self.plots[n], d[k]) for n in p['neighbors']) for k in (('base',) if mode == 'base' else ('base', 'spec'))):
                    after[c, q].add(i)
        return after

    def run(self):
        order = [(c, q) for c in self.ids for q in PROBABILITIES]
        self.rng.shuffle(order)
        current = self.baseline_sites
        for c, q in order:
            roll = random.Random(stable_seed(self.seed, self.source['settings']['map_seed'], c, q, 'assist')).random()
            attempt = {'continent': c, 'quarter': q, 'probability': PROBABILITIES[q], 'roll': roll}
            self.attempts.append(attempt)
            if current[c, q]: attempt['outcome'] = 'already covered'; continue
            if roll >= PROBABILITIES[q]: attempt['outcome'] = 'not selected'; continue
            option = self.choose(self.options(c, q, current), c, q, current)
            if option is None: attempt['outcome'] = 'no safe feasible repair within budget'; continue
            deposits = option['deposits']
            for i, r in deposits:
                assert self.rules.can_place(self.plots[i], r, self.plots)
                self.plots[i]['resource'] = r
            after = self.sites_local(deposits, current)
            self.base_sites = self.sites_local(deposits, self.base_sites, mode='base')
            assert after[c, q]
            gains = [{'continent': cid, 'quarter': industry, 'sites': len(v)} for (cid, industry), v in after.items() if v and not current[cid, industry]]
            for i, r in deposits:
                p = self.plots[i]
                self.additions.append({'number': len(self.additions) + 1, 'plot': i, 'x': p['x'], 'y': p['y'],
                                       'resource': r, 'continent': c, 'quarter': q,
                                       'material_class': ' + '.join(k for k in ('base', 'spec') if r in self.definitions[q][k].get('resources', [])),
                                       'center': option['center'], 'repair_size': len(deposits), 'coverage_gains': gains})
                self.budget[c] += 1
            self.reserved_centers.add(option['center'])
            attempt['outcome'] = 'added'; attempt['plots'] = [i for i, _ in deposits]
            current = after
        assert current == self.sites()
        return self.package(current)

    def package(self, sites):
        census = continent_census(self.data, self.definitions)
        original = self.source
        counts = {q: {'before': sum(bool(self.baseline_sites[c, q]) for c in self.ids),
                      'after': sum(bool(sites[c, q]) for c in self.ids)} for q in self.definitions}
        return {**{k: copy.deepcopy(v) for k, v in original.items() if k not in ('data', 'continents', 'reference', 'source_sha256')},
                'id': f"csc-assist-{original['number']}", 'group': 'csc-assist', 'groupLabel': 'CSC helper · preview additions',
                'data': self.data, 'continents': census, 'reference': census[0]['quarters'],
                'provenance': {'native': False, 'kind': 'assistance-preview', 'seed': self.seed,
                               'warning': 'Preview additions on a captured native map. Original deposits and terrain preserved. Habitat checks use calibrated offline rules; native placement and mod execution remain to be tested.',
                               'source_sha256': original['source_sha256']},
                'assistance': {'source_id': original['id'], 'seed': self.seed, 'additions': self.additions,
                               'attempts': self.attempts, 'coverage': counts,
                               'palettes': [{'continent': c, 'quarter': q, 'kind': k, 'resource': r} for (c, q, k), r in sorted(self.palette.items())],
                               'before_continents': original['continents']}}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--database', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--seed', type=int, default=SEED)
    args = p.parse_args()
    bundle = read(args.bundle)
    originals = [m for m in bundle['maps'] if m['group'] == 'luxuries-4']
    assert len(originals) == 5
    original_hashes = {m['id']: hashlib.sha256(json.dumps(m, sort_keys=True).encode()).hexdigest() for m in originals}
    rules = Rules(args.database)
    previews = [Helper(m, rules, args.seed).run() for m in originals]
    assert all(hashlib.sha256(json.dumps(m, sort_keys=True).encode()).hexdigest() == original_hashes[m['id']] for m in originals)
    bundle['maps'] = [m for m in bundle['maps'] if m['group'] != 'csc-assist'] + previews
    bundle['default_group'] = 'csc-assist'
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'maps.json').write_text(json.dumps(bundle, separators=(',', ':')), encoding='utf-8')
    render(bundle, args.output / 'index.html')
    (args.output / 'preview-maps.json').write_text(json.dumps({'maps': previews}, separators=(',', ':')), encoding='utf-8')
    rows = [{'map': m['number'], **a} for m in previews for a in m['assistance']['additions']]
    write_csv(args.output / 'added-resources.csv', [{k: v for k, v in a.items() if k != 'coverage_gains'} for a in rows])
    coverage = {q: {k: sum(m['assistance']['coverage'][q][k] for m in previews) for k in ('before', 'after')} for q in originals[0]['definitions']}
    result = {'seed': args.seed, 'maps': 5, 'continents': 15, 'coverage': coverage,
              'additions_per_map': {m['number']: len(m['assistance']['additions']) for m in previews},
              'probabilities': PROBABILITIES, 'budget': {'per_continent': 4, 'per_map': 10},
              'database_sha256': hashlib.sha256(args.database.read_bytes()).hexdigest(),
              'source_maps': {m['id']: m['source_sha256'] for m in originals}}
    (args.output / 'assistance-analysis.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    write_csv(args.output / 'coverage-comparison.csv', [{'quarter': q, **values, 'target': 5 if q == 'GOLDSMITHS' else 10} for q, values in coverage.items()])
    print(json.dumps(result))


if __name__ == '__main__':
    main()
