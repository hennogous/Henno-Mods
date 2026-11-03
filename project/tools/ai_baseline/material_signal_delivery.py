"""Interpret acquisition/private-signal controls without conflating Lua domains.

A getter that does not expose even the already-owned positive control cannot be
used to declare failure on the acquired tile. A yield response is never an AI
choice, path, preservation action or consumption proof.
"""

def summarize_domain(contrasts, *, expected=80, required=6):
    assert expected > 0 and required > 0
    observed = len(contrasts)
    complete = observed == required and all(
        isinstance(v.get('owned_control_delta'), (int, float)) and
        isinstance(v.get('newly_acquired_delta'), (int, float)) for v in contrasts)
    positive = complete and all(v['owned_control_delta'] == expected for v in contrasts)
    if not complete:
        state = 'incomplete_or_missing_observations'
    elif not positive:
        state = 'no_consistent_positive_control'
    elif all(v['newly_acquired_delta'] == expected for v in contrasts):
        state = 'acquired_response_matches_positive_control'
    elif all(v['newly_acquired_delta'] == 0 for v in contrasts):
        state = 'acquired_response_absent_with_positive_control'
    else:
        state = 'mixed_acquired_response'
    return dict(state=state, observed=observed, required=required,
                positive_control_verified=positive,
                acquired_delivery_comparison_informative=positive,
                native_AI_consumption_proven=False,
                ownership_registration_cause_proven=False)


def report(audit):
    assert audit['verified'] and audit['zero_AI_turns'] and audit['one_load_original16']
    assert audit['private_properties_restored'] and audit['runtime510_restored']
    domains = {k: summarize_domain(v['contrasts']) for k, v in audit['delivery'].items()}
    assert set(domains) == {'Core', 'UI'}
    return dict(verified_controlled_observation=True, domains=domains,
                Core_UI_must_remain_distinct=True,
                native_modifier_subject_reader_errors=audit['modifier_reader_errors'],
                next_question='Measure the same on/off contrast through native city-level private yields and unchanged worked-plot inputs before diagnosing collection registration or changing the backend.',
                current_backend='assisted quoted city assignment and treasury debit; native AI PURCHASE unproven',
                AI_material_preservation_influence_proven=False,
                limits=['A zero response without a positive control is inconclusive.',
                        'These observations do not identify a native task score or Builder decision.',
                        'One diagnostic purchase is excluded from accepted game outcome totals.'])
