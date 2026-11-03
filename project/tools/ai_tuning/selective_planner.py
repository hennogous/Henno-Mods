"""Small offline start policy over the existing strict site evaluator.

This is a shortlist for investment review, never a command or spending authority.
Both or combined real P/G >=4 is an explicit trial policy, not calibrated ROI.
Future development must already satisfy the evaluator's evidence gates.
"""
from copy import deepcopy
from itertools import combinations
from site_evaluator import evaluate_site, current_dominance, value, YIELDS


def shortlist(sites, mapping, combined_threshold=4):
    if isinstance(combined_threshold, bool) or combined_threshold not in (3, 4, 5):
        raise ValueError('Use a declared +3/+4/+5 trial threshold')
    rows, keys, context = [], set(), None
    for site in sites:
        evaluated = evaluate_site(site, mapping)
        ident = evaluated['identity']
        current_context = (ident['player'], ident['turn'])
        if context is not None and current_context != context:
            raise ValueError('Mixed player/clock in a planning batch')
        context = current_context
        key = (ident['city'], evaluated['quarter'], ident['plot'])
        if key in keys:
            raise ValueError('Duplicate start alternative')
        keys.add(key)
        reasons = []
        if value(site.get('configured_ai')) is False:
            status = 'excluded_original_human'
        elif value(site.get('configured_ai')) is not True:
            status = 'defer_missing_evidence'
            reasons.append('stable original-human exclusion unavailable')
        elif evaluated['rejections']:
            status = 'infeasible'
            reasons.extend(evaluated['rejections'])
        elif evaluated['unknowns'] or not evaluated['future_coverage_complete']:
            status = 'defer_missing_evidence'
            reasons.extend(evaluated['unknowns'])
        elif evaluated['recommendation'] == 'tradeoff_review' or value(site.get('build_commitment')) != 'new':
            status = 'compare_existing_commitments_or_displacement'
            reasons.append('Do not open a new chain before resolving recorded alternatives or commitments')
        else:
            roles = set(evaluated['current_supply'])
            for plan, decision in zip(site.get('future', []), evaluated['future']):
                if plan['kind'] == 'material' and decision['status'] == 'credible_conditional':
                    for material in evaluated['materials']:
                        if material['plot'] == plan['plot']:
                            roles.update(material['roles'])
            both = evaluated['both_service_potential']['with_credible_development']
            combined = sum(evaluated['current'][y] + evaluated['credible_future_increment'][y] for y in YIELDS)
            if 'base' not in roles:
                status = 'decline_no_credible_base'
            elif not both and combined < combined_threshold:
                status = 'decline_below_trial_threshold'
            else:
                status = 'shortlisted_for_investment_review'
                reasons.append('Both supply option' if both else 'combined real P/G meets trial threshold')
        rows.append(dict(identity=deepcopy(ident), quarter=evaluated['quarter'], status=status,
                         reasons=reasons, evaluation=evaluated))
    # Eliminate only demonstrably dominated same-context alternatives. Different
    # future plans, materials or displaced customer options are not interchangeable.
    comparisons, dominated = [], set()
    for (ai, a), (bi, b) in combinations(enumerate(rows), 2):
        if a['status'] != 'shortlisted_for_investment_review' or b['status'] != a['status']:
            continue
        ab = current_dominance(a['evaluation'], b['evaluation'])
        ba = current_dominance(b['evaluation'], a['evaluation'])
        comparisons.append(dict(first=dict(identity=a['identity'], quarter=a['quarter']),
                                second=dict(identity=b['identity'], quarter=b['quarter']),
                                first_over_second=ab, second_over_first=ba))
        if ab == 'a_current_vector_dominates':
            dominated.add(bi)
        if ba == 'a_current_vector_dominates':
            dominated.add(ai)
    for index, row in enumerate(rows):
        if index in dominated:
            row['status'] = 'dominated_same_context'
    return dict(policy=dict(base_required=True, both_or_combined=combined_threshold),
                alternatives=rows, comparisons=comparisons,
                shortlist=[dict(identity=r['identity'], quarter=r['quarter']) for r in rows if r['status']=='shortlisted_for_investment_review'],
                allocation='unallocated; cross-site conflicts, empire budget and execution still require review',
                action_authorization=False)
