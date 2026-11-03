"""Read-only geometry evidence, separate from investment execution readiness.

This adapter never feeds fabricated capacity/costs/native bindings to the strict
site evaluator. Native preview, computed CSC real and private units stay distinct.
"""
from copy import deepcopy
from itertools import combinations
from math import isfinite

YIELDS = ('YIELD_PRODUCTION', 'YIELD_GOLD')


def numeric(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and isfinite(v)


def review(raw, source):
    if not source or (raw.get('player'), raw.get('city'), raw.get('turn')) != (3, 131073, 110):
        raise ValueError('Declared native identity/provenance mismatch')
    if raw.get('action_authorization') is not False or raw.get('execution_readiness') != 'unknown':
        raise ValueError('Shadow evidence cannot authorize action')
    tiles = {t['plot']: t for t in raw['tiles']}
    expected = {(q, t['plot']) for q, s in raw['district_state'].items()
                for t in s['targets'] if t['legal'] is True}
    keys = [(s['quarter'], s['plot']) for s in raw['candidates']]
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise ValueError('Native opportunity set incomplete or duplicated')
    result = dict(source=source, action_authorization=False, execution_readiness='unknown',
                  opportunities=[], comparisons=[], conflicts=[], limitations=[],
                  native_positive_controls=[], source_capture=deepcopy(raw))
    if raw.get('enrichment_complete') is not True:
        result['limitations'].append('existing-chain dependencies/controls incomplete: ' + str(raw.get('enrichment_error', 'candidate stage only')))
    dependencies = {}
    for c in raw['chains']:
        for p in c['dependencies']:
            dependencies.setdefault(p, []).append({k: c[k] for k in ('city', 'quarter', 'plot')})
    for s in raw['candidates']:
        t = tiles[s['plot']]
        row = deepcopy(s)
        row['source'] = source + f"#/candidates/{raw['candidates'].index(s)}"
        row['river'] = t['river']
        row['materials'] = []
        row['customer_geometry'] = []
        row['adjacent_district_geometry'] = []
        customer_types = {r['index'] for r in s['mapped_customer_types']}
        row['footprint_loss'] = deepcopy(t)
        row['future_execution'] = 'unknown; no delay/capacity/access/valuation credit'
        for p in t['neighbors']:
            if p not in tiles:
                raise ValueError('Candidate neighbor scope incomplete')
            n = tiles[p]
            roles = n['roles'][s['quarter']]
            if roles['base'] or roles['specialty']:
                material = deepcopy(n)
                material['supply_predicate_projection'] = (
                    n['owner'] == raw['player'] and n['resource_visible'] is True
                    and n['valid_resource_improvement'] is True
                    and n['improvement_pillaged'] is False and n['district'] < 0)
                material['native_bound_candidate_modifier'] = 'unavailable before placement'
                material['predicate_scope'] = 'adjacent player-owned mapped functioning improvement; not same-city purchase ownership; no worked-tile requirement assumed'
                row['materials'].append(material)
            if n['district'] >= 0:
                adjacent = deepcopy(n)
                adjacent['mapped_customer_match'] = n['district'] in customer_types
                row['adjacent_district_geometry'].append(adjacent)
                if adjacent['mapped_customer_match']:
                    row['customer_geometry'].append(deepcopy(adjacent))
        if s['plot'] in dependencies:
            result['conflicts'].append(dict(kind='footprint_on_existing_chain_material',
                candidate=[s['quarter'], s['plot']], chains=dependencies[s['plot']], loss_value='unknown'))
        native = s['preview']['native']
        if not all(numeric(native.get(y)) for y in YIELDS):
            result['limitations'].append('native candidate P/G unavailable at ' + repr((s['quarter'], s['plot'])))
        result['opportunities'].append(row)
    # Local vector comparisons describe components, never a utility or ROI rank.
    for a, b in combinations(result['opportunities'], 2):
        if a['quarter'] != b['quarter']:
            if a['plot'] == b['plot']:
                result['conflicts'].append(dict(kind='mutually_exclusive_footprint', candidates=[[a['quarter'], a['plot']], [b['quarter'], b['plot']]]))
            continue
        vectors = {}
        for component in ('native', 'computed_real'):
            av, bv = a['preview'][component], b['preview'][component]
            if all(numeric(v.get(y, 0) if component == 'computed_real' else v.get(y)) for v in (av, bv) for y in YIELDS):
                vectors[component] = {y: av.get(y, 0) - bv.get(y, 0) for y in YIELDS}
        result['comparisons'].append(dict(quarter=a['quarter'], plots=[a['plot'], b['plot']],
            component_delta_first_minus_second=vectors, preference='deferred; supply/customer/footprint and execution costs differ or are unknown'))
    for c in raw['controls']:
        native, existing = c['preview']['native'], c['existing_adjacency']
        matched = all(numeric(native.get(y)) and numeric(existing.get(y)) and native[y] == existing[y] for y in YIELDS)
        positive = matched and any(native[y] > 0 for y in YIELDS)
        result['native_positive_controls'].append(dict(city=c['city'], plot=c['plot'], matched=matched, positive=positive,
            status='positive_matching' if positive else 'zero_matching' if matched else 'unavailable_or_disagrees',
            native=deepcopy(native), existing_adjacency=deepcopy(existing), existing_total=deepcopy(c['existing_total'])))
    result['native_accessor_positive'] = any(c['positive'] for c in result['native_positive_controls'])
    result['comparative_geometry_observed'] = bool(result['comparisons'] or result['conflicts'])
    result['opportunity_count'] = len(keys)
    result['status'] = 'geometry_observed_execution_unknown' if result['native_accessor_positive'] and not result['limitations'] and result['comparative_geometry_observed'] else 'partial_geometry_no_extension'
    return result
