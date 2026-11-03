"""Bounded offline Quarter evidence evaluator. No native imports or side effects.

Evidence is {value: ..., source: nonempty string}. Missing/unsourced evidence
is unknown. Caller supplies a validated, enabled mapping snapshot, never guessed
resource names. This is recommendation evidence, not an action authority.
"""
from __future__ import annotations
from copy import deepcopy
from collections import Counter
from math import isfinite

YIELDS = ('YIELD_PRODUCTION', 'YIELD_GOLD')
GATES = ('legal', 'unlocked', 'accessible', 'capacity_supported', 'affordable')
COSTS = ('acquisition_gold', 'own_gold', 'subsidy_gold', 'production', 'builder_charges', 'travel_turns',
         'maintenance', 'lost_tile_value', 'district_capacity_used')


def value(fact):
    return fact.get('value') if isinstance(fact, dict) and fact.get('source') else None


def number(fact):
    n = value(fact)
    return n if isinstance(n, (int, float)) and not isinstance(n, bool) and isfinite(n) else None


def comparable(data):
    """Compare evidenced meaning, retaining context but excluding source locations."""
    if isinstance(data, dict):
        return {k: comparable(v) for k, v in data.items() if k != 'source'}
    if isinstance(data, list):
        return [comparable(v) for v in data]
    return data


def mapping_relations(mapping, quarter):
    """Use explicit TypeTags and Improvement_ValidResources row evidence.

    quarter_classes maps the Quarter's base/specialty tags. Validation here
    checks envelope/row integrity, not the source database's correctness.
    """
    if value(mapping.get('validated')) is not True or not mapping.get('snapshot'):
        raise ValueError('A validated enabled mapping snapshot is required')
    classes = mapping['quarter_classes'][quarter]
    tags = mapping['TypeTags']
    improvements = mapping['Improvement_ValidResources']
    for row in tags + improvements:
        if not row.get('source'):
            raise ValueError('Mapping row lacks provenance')
    relations = {}
    for row in tags:
        for role in ('base', 'specialty'):
            if row['Tag'] == classes[role]:
                relations.setdefault(row['Type'], set()).add(role)
    valid = {(r['ResourceType'], r['ImprovementType']) for r in improvements}
    return relations, valid


def band(production, gold):
    if production is None or gold is None:
        return 'unknown'
    combined = production + gold
    return '+5_or_more' if combined >= 5 else '+4' if combined >= 4 else '+3' if combined >= 3 else 'below_+3'


def evaluate_site(site, mapping):
    """Return a transparent fact vector; no currency conversion or weighted score.

    Future increments must be marginal real P/G beyond current observations.
    They are shown only after every gate plus positive delay is evidenced;
    discount is qualitative (delayed/conditional), not invented yield precision.
    Both describes mapped supply potential, never active Service guarantees.
    """
    relations, valid = mapping_relations(mapping, site['quarter'])
    result = {'identity': deepcopy(site['identity']), 'quarter': site['quarter'],
              'mapping_snapshot': mapping['snapshot'], 'unknowns': [], 'rejections': [],
              'mapping_provenance': deepcopy(mapping),
              'reasons': [], 'future': [], 'costs': {}, 'material_footprint_loss': [],
              'customer_alternatives': deepcopy(site.get('customer_alternatives', [])),
              'existing_unfinished_chains': deepcopy(site.get('existing_unfinished_chains')),
              'current': {}, 'materials': [], 'provenance': deepcopy(site)}
    unknown, reject = result['unknowns'], result['rejections']
    if not site['identity'].get('source'):
        unknown.append('identity provenance')
    for field in ('player', 'city', 'turn', 'plot'):
        identity_value = site['identity'].get(field)
        if not isinstance(identity_value, int) or isinstance(identity_value, bool) or identity_value < 0:
            unknown.append('identity ' + field)
    for gate in GATES:
        v = value(site.get(gate))
        if v is False:
            reject.append('site ' + gate)
        elif v is not True:
            unknown.append('site ' + gate)
    for y in YIELDS:
        result['current'][y] = number(site.get('current_real', {}).get(y))
        if result['current'][y] is None:
            unknown.append('current real ' + y)
    result['current']['band'] = band(*(result['current'][y] for y in YIELDS))
    result['current']['river'] = deepcopy(site.get('river'))
    result['current']['customers'] = deepcopy(site.get('current_customers'))
    for field in ('river', 'current_customers', 'built_stages', 'existing_unfinished_chains',
                  'build_commitment', 'customer_alternatives', 'material_inventory_complete'):
        if value(site.get(field)) is None:
            unknown.append(field)
    if value(site.get('material_inventory_complete')) is not True:
        unknown.append('complete material inventory required')
    # Resource roles come only from the mapping; unrelated bonus resources add nothing.
    current_roles, possible_roles = set(), set()
    footprint = site['identity'].get('plot')
    for material in site.get('materials', []):
        roles = relations.get(material['resource'], set())
        if not material.get('source'):
            unknown.append(f'material resource provenance {material["plot"]}')
        footprint_roles = []
        if material['plot'] == footprint:
            for q, classes in mapping['quarter_classes'].items():
                for tag in mapping['TypeTags']:
                    for role in ('base', 'specialty'):
                        if tag['Type'] == material['resource'] and tag['Tag'] == classes[role]:
                            footprint_roles.append({'quarter': q, 'role': role})
        row = {'plot': material['plot'], 'resource': material['resource'], 'roles': sorted(roles),
               'state': 'unrelated', 'source': material.get('source')}
        if footprint_roles:
            result['material_footprint_loss'].append({**row, 'affected_roles': footprint_roles,
                                                      'loss_extent': 'mapped resource removed; dependent chain loss requires evidence'})
        if roles:
            if material['plot'] == footprint:
                row['state'] = 'lost_to_footprint'
            elif not material.get('source') or value(material.get('adjacent')) is not True:
                row['state'] = 'unknown'
                unknown.append(f'material adjacency/provenance {material["plot"]}')
            elif value(material.get('improved_working')) is True and (material['resource'], material.get('improvement')) in valid:
                eligible = value(material.get('supply_eligible'))
                expected_context = {'player':site['identity'].get('player'),
                                    'city':site['identity'].get('city'), 'quarter':site['quarter']}
                if value(material.get('supply_context')) != expected_context:
                    eligible = None
                if eligible is True:
                    row['state'] = 'current_supply'
                    current_roles.update(roles)
                    possible_roles.update(roles)
                else:
                    row['state'] = 'ineligible_supply' if eligible is False else 'unknown_supply_eligibility'
                    if eligible is None:
                        unknown.append(f'native bound supply eligibility {material["plot"]}')
            else:
                row['state'] = 'needs_development'
                if value(material.get('improved_working')) is None:
                    row['state'] = 'unknown_improvement_state'
                    unknown.append(f'material improvement state {material["plot"]}')
        result['materials'].append(row)
    plot_counts = Counter(p['plot'] for p in site.get('future', []))
    future_p, future_g = 0, 0
    for plan in site.get('future', []):
        issues = []
        if not plan.get('source'):
            issues.append('unknown provenance')
        for gate in GATES:
            v = value(plan.get(gate))
            if v is not True:
                issues.append(('rejected ' if v is False else 'unknown ') + gate)
        delay = number(plan.get('delay_turns'))
        if delay is None or delay <= 0:
            issues.append('unknown positive development delay')
        plot = plan['plot']
        if plot == footprint or plot_counts[plot] > 1:
            issues.append('conflicting future plot')
        roles = set()
        if plan['kind'] == 'material':
            roles = relations.get(plan.get('resource'), set())
            if not roles or (plan.get('resource'), plan.get('improvement')) not in valid:
                issues.append('unmapped resource/improvement')
            if value(plan.get('adjacent')) is not True:
                issues.append('unknown material adjacency')
            observed = [m for m in site.get('materials', []) if m['plot'] == plot
                        and m.get('source') and m.get('resource') == plan.get('resource')]
            if len(observed) != 1:
                issues.append('unknown unique observed resource on future material plot')
        elif plan['kind'] != 'customer':
            issues.append('unsupported future kind')
        if plan['kind'] == 'customer' and value(plan.get('mapped_customer')) is not True:
            issues.append('unknown customer mapping')
        if plan['kind'] == 'customer' and value(plan.get('adjacent')) is not True:
            issues.append('unknown customer adjacency')
        increments = {y: number(plan.get('incremental_real', {}).get(y)) for y in YIELDS}
        if any(v is None or v < 0 for v in increments.values()):
            issues.append('unknown/nonincremental real yields')
        for cost in COSTS:
            n = number(plan.get('costs', {}).get(cost))
            if n is None or n < 0:
                issues.append('unknown cost ' + cost)
        status = 'withheld' if issues else 'credible_conditional'
        result['future'].append({'plot': plot, 'kind': plan['kind'], 'status': status,
                                 'issues': issues, 'delay_turns': delay,
                                 'incremental_real': increments if not issues else None,
                                 'discount': 'delayed and conditional; not realised' if not issues else 'no credit'})
        if not issues:
            possible_roles.update(roles)
            future_p += increments[YIELDS[0]]
            future_g += increments[YIELDS[1]]
        else:
            unknown.extend(f'future {plot}: {issue}' for issue in issues if issue.startswith('unknown'))
    for cost in COSTS:
        result['costs'][cost] = number(site.get('costs', {}).get(cost))
        if result['costs'][cost] is None or result['costs'][cost] < 0:
            result['costs'][cost] = None
            unknown.append('cost ' + cost)
    p, g = (result['current'][y] for y in YIELDS)
    result['credible_future_increment'] = dict(zip(YIELDS, (future_p, future_g)))
    result['future_coverage_complete'] = all(x['status'] != 'withheld' for x in result['future'])
    result['future_total_increment'] = deepcopy(result['credible_future_increment']) if result['future_coverage_complete'] else None
    result['projected_band'] = band(None if p is None else p + future_p, None if g is None else g + future_g)
    result['current_supply'] = sorted(current_roles)
    result['both_service_potential'] = {'current_mapped_supply': {'base', 'specialty'} <= current_roles,
        'with_credible_development': {'base', 'specialty'} <= possible_roles,
        'active_service': None, 'explanation': 'Supply option only; producer/customer buildings and Service gates remain separate'}
    result['reasons'].append('Combined bands add real Production and Gold for description only; no exchange rate or ROI')
    result['reasons'].append('Compare finishing/repairing existing chains before a new commitment')
    # These are review categories, not tuned placement thresholds or action permissions.
    if reject:
        result['recommendation'] = 'infeasible'
    elif unknown or any(x['status'] == 'withheld' for x in result['future']):
        result['recommendation'] = 'insufficient_evidence'
    elif result['material_footprint_loss'] or value(site.get('existing_unfinished_chains')) or value(site.get('customer_alternatives')):
        result['recommendation'] = 'tradeoff_review'
    elif not ({'base'} <= possible_roles):
        result['recommendation'] = 'marginal_no_mapped_base'
    elif result['both_service_potential']['with_credible_development'] or result['projected_band'] in ('+3', '+4', '+5_or_more'):
        result['recommendation'] = 'promising_review'
    else:
        result['recommendation'] = 'marginal_review'
    return result


def current_dominance(a, b):
    """Conservative, local comparison only; no future/Service utility assumption.

    Full-site dominance requires same context, no unresolved tradeoffs and equal
    explicit future plans/material roles/commitments. Unknowns make it undecidable.
    """
    if a['unknowns'] or b['unknowns'] or a['rejections'] or b['rejections']:
        return 'undetermined'
    for key in ('quarter', 'mapping_snapshot', 'future', 'current_supply',
                'both_service_potential', 'material_footprint_loss',
                'customer_alternatives', 'existing_unfinished_chains'):
        if comparable(a[key]) != comparable(b[key]):
            return 'undetermined'
    for key in ('player', 'city', 'turn'):
        if a['identity'].get(key) != b['identity'].get(key):
            return 'undetermined'
    for key in ('build_commitment', 'built_stages', 'river', 'current_customers'):
        if value(a['provenance'].get(key)) != value(b['provenance'].get(key)):
            return 'undetermined'
    av = [a['current'][y] for y in YIELDS] + [-a['costs'][k] for k in COSTS]
    bv = [b['current'][y] for y in YIELDS] + [-b['costs'][k] for k in COSTS]
    return 'a_current_vector_dominates' if all(x >= y for x, y in zip(av, bv)) and any(x > y for x, y in zip(av, bv)) else 'no_dominance'


def archive_coverage(casepack):
    """Adapt actual cases as evidence/gaps, never synthesize missing Quarter facts."""
    cases = casepack['cases']
    return {'source_files': deepcopy(casepack['source_files']), 'source_turn': casepack['source_turn'],
            'coimbra_customer_alternatives': deepcopy(cases['coimbra_harbor']['options']),
            'repair_needs': deepcopy(cases['material_repair']),
            'lost_supply_commitment_case': deepcopy(cases['maize_1863']),
            'evaluated_quarter_sites': 0,
            'reason': 'Archive contains customer opportunities and repair/commitment evidence, not complete Quarter evaluator inputs',
            'missing': ['validated enabled mapping snapshot', 'current real Quarter Production/Gold decomposition',
                        'future legal/unlocked/access/capacity/affordability and delay', 'whole-chain costs',
                        'complete material inventory and customer alternatives', 'existing chain completion/repair alternatives']}
