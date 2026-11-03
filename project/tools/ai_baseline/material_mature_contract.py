"""Strict source boundary for an audited mature material-access continuation.

Missing parent unit/observer-treasury references are explicit. A fresh before/after
census proves setup had no native effect; it cannot fill historical missingness.
Care job ages reset on reload; this never authorizes a world or yield change.
"""
from full_game_controller.continuation import world_signature


def ordered(value):
    if isinstance(value, dict):
        return {str(k): ordered(v) for k, v in sorted(value.items(), key=lambda x: str(x[0]))}
    if isinstance(value, list):
        import json
        return sorted((ordered(v) for v in value), key=lambda v: json.dumps(v, sort_keys=True))
    return value


def source_gate(*, parent_world, world, parent_cash, gold, parent_allocation,
                allocation, parent_builders, builders, parent_care, care):
    assert parent_world['turn'] == world['turn'] == 75
    assert not parent_world['errors'] and not world['errors']
    assert world_signature(parent_world) == world_signature(world), 'World/physical state changed'
    # Ordinary city outputs and recipient properties are source inputs too.
    city = lambda s: ordered([{k: c.get(k) for k in ('player', 'id', 'yields', 'properties')}
                              for c in s['cities']])
    assert city(parent_world) == city(world), 'City economy/properties changed'
    expected = {str(v['player']): v['gold'] for v in parent_cash['players']}
    assert set(expected) == {str(p) for p in range(1, 6)}
    assert all(gold.get(p) == v for p, v in expected.items()), 'AI treasury changed'
    assert allocation['turn'] in (74, 75) and parent_allocation['turn'] in (74, 75)
    assert ordered(parent_allocation['cities']) == ordered(allocation['cities']), 'Private/economic/citizen input changed'
    assert parent_builders['turn'] == builders['turn'] == 75
    assert not parent_builders['errors'] and not builders['errors']
    assert ordered(parent_builders['players']) == ordered(builders['players']), 'Builder unit/charge/position changed'
    assert parent_care['version'] == care['version'] == 3 and not care['errors']
    assert parent_care['policy'] == care['policy']
    assert care['turn'] == 75
    reset = []
    for pid, row in care['players'].items():
        old = parent_care['players'][pid]
        # Ages/counters may reset; physical state and mapped links may not.
        fields = ('plot', 'state', 'resource', 'rank', 'links')
        project = lambda x: ordered([{k: p.get(k) for k in fields} for p in x['plots']])
        assert project(old) == project(row), ('Material source state changed', pid)
        assert all(p.get('ready_age', 0) == 0 and not p.get('urgent', False) for p in row['plots'])
        assert not row['work_urgent'] and row['urgent_jobs'] == 0
        reset.append({'player': int(pid), 'old_urgent': old['work_urgent'],
                      'new_urgent': row['work_urgent'], 'age_boundary_censored': True})
    return dict(verified=True, turn=75, full_world=True, AI_gold=True,
                private_economic_and_citizen_inputs_equal=True, Builder_inventory_equal=True,
                care_reload_reset=reset, full_parent_nonBuilder_inventory='UNOBSERVED',
                parent_observer0_treasury='UNOBSERVED', reconstructed_sites=0,
                pre75_AI_replay=0, new_worlds=0)


def no_setup_effect(before, after):
    assert before['world']['turn'] == after['world']['turn'] == 75
    # Observer events are intentionally restored from the parent; they are not
    # world effects. Every other native census field must remain identical.
    native_world = lambda s: {k: v for k, v in s.items() if k != 'events'}
    assert ordered(native_world(before['world'])) == ordered(native_world(after['world'])), 'Observer setup changed world'
    for k in ('units', 'gold'):
        assert ordered(before[k]) == ordered(after[k]), ('Observer setup changed native state', k)
    return dict(verified=True, fresh_units_and_all_major_gold_equal=True,
                historical_missing_references_not_filled=True)


def production_gate(parent_gameplay, parent_UI, gameplay, UI, *, reason):
    assert gameplay['targets'] == parent_gameplay['targets']
    assert not gameplay['errors'] and not UI['errors']
    for current, old, fields in (
        (gameplay, parent_gameplay, ('owner', 'district_type', 'district_present', 'complete', 'current', 'queue', 'population')),
        (UI, parent_UI, ('cost', 'progress', 'current_hash', 'queue', 'queue_size', 'has_been_placed')),
    ):
        key = lambda x: (x['player'], x['city'], x['plot'])
        a = {key(x): x for x in current['history'] if x['reason'] == reason}
        b = {key(x): x for x in old['history'] if x['reason'] == 'diagnostic75-final'}
        assert a.keys() == b.keys() and len(a) == len(parent_gameplay['targets'])
        assert all(all(a[k].get(f) == b[k].get(f) for f in fields) for k in a), 'Production parity failed'
    return dict(verified=True, physical_UI_sites=len(gameplay['targets']), queues_and_costs_equal=True)


def endpoint_action_gate(rows):
    assert all(v.get('turn', v.get('request', {}).get('turn', -1)) < 75
               for v in rows if v['event'] in ('foundation-begin', 'foundation-confirmed',
                                               'funded-acquisition-begin', 'funded-acquisition-confirmed'))
    return dict(parent75_capture_only=True, first_new_cycle=75, source75_and_postcycle75_distinct=True)
