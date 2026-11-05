"""Calibrate two measured forecast errors for an inland, flat Bakers site.

The input is the reconciled output of mill_building_study/analyze.py. The
caller must independently prove the plot is inland, flat, and a legal,
revealed, owned, unoccupied native candidate for this city. The analyzer's
aggregation rows omit geometry and the native eligibility flags. The result
applies to this exact calculation.
"""

BAKERS = 'DISTRICT_CSC_BAKERS_QUARTER'
WIND = 'BUILDING_CSC_BAKERS_WIND_MILL'
WATER = 'BUILDING_CSC_BAKERS_WATER_MILL'
BAKERY = 'BUILDING_CSC_BAKERS_BAKERY'
CAFE = 'BUILDING_CSC_BAKERS_CAFE'
WIND_CHILD = 'MOD_CSC_ADJ_CSC_BAKERS_WIND_MILL_PRODUCTION_FROM_HILLS_STEP_1'
WIND_ROOT = 'ATTACH_' + WIND_CHILD
WATER_ROOTS = {
    'MOD_CSC_BAKERS_GOLD_TO_WATER_MILL': 'YIELD_GOLD',
    'MOD_CSC_BAKERS_PROD_TO_WATER_MILL': 'YIELD_PRODUCTION',
}
MAX_SCORE = 2**31 - 1


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def one(records, matches, name):
    result = [record for record in records if matches(record)]
    require(len(result) == 1, f'Expected exactly one {name}, found {len(result)}')
    return result[0]


def positive_q8(value):
    return type(value) is int and 0 < value <= MAX_SCORE


def calibrate(analysis, *, player=1, city=65536, plot=1210) -> dict:
    """Replace erroneous admitted credit using the original positive gate.

    For each admitted building, subtract only its measured invalid roots and
    then repeat the positive raw-building gate. Other terms and the native
    district site's pre-aggregation value remain outside the correction.
    """
    require(analysis['schema'] == 1 and analysis['profile'] == 'mill-building-study-v1'
            and all(analysis[key] is True for key in (
                'ok', 'integrity_complete', 'modifier_accounting_complete',
                'source_state_aggregation_complete')), 'Incomplete or unsupported analysis')
    calc = one(analysis['district_aggregations'],
               lambda record: (record['player'], record['city']) == (player, city),
               'target city calculation')
    district = one(calc['districts'], lambda record: record['type'] == BAKERS,
                   'Bakers aggregation')
    require(district['status'] == 'exact_source_state_aggregation_match'
            and district['source_gate_unknown'] is False,
            'Bakers aggregation does not reconcile')
    row = one(district['rows'], lambda record: record['plot'] == plot, 'target plot row')
    before, native = row['before_q8'], row['after_q8']
    require(row['row'] > 0 and positive_q8(before) and positive_q8(native)
            and row['matches'] is True and row['source_derived_after_q8'] == native
            and row['raw_aliases_mutable_before'] is True
            and row['raw_aliases_mutable_after'] is True
            and (row['raw_before_q8'], row['raw_after_q8']) == (before, native),
            'Target is not a reconciled positive noncenter score row')

    admitted = [record for record in district['buildings']
                if record['admitted_by_source_gates'] is True]
    require(sorted(record['type'] for record in admitted) == sorted((WIND, BAKERY, CAFE)),
            'Expected Wind, Bakery, and Café as the sole admitted buildings')
    water = one(district['buildings'], lambda record: record['type'] == WATER,
                'excluded Water Mill building')
    require(water['admitted_by_source_gates'] is False
            and 'lower_index_mutual_canonical:' + WIND in water['reasons'],
            'Expected Water Mill to be omitted by the native alternative gate')
    raw_total = sum(record['raw_q8'] for record in admitted)
    require(raw_total == district['source_derived_sum_q8'] == row['delta_q8']
            and before + raw_total == native, 'Raw building sum differs from the actual row uplift')

    results, receipts = [], []
    for entry in admitted:
        name, raw = entry['type'], entry['raw_q8']
        component = one(analysis['building_components'],
                        lambda record: record['id'] == entry['latest_building_call_id'],
                        f'{name} building forecast')
        require(entry['latest_value_matches_raw'] is True and positive_q8(raw)
                and calc['raw_building_before_q8'][name] == raw
                and (component['player'], component['city'], component['type'],
                     component['building'], component['value_q8']) == (
                         player, city, name, entry['index'], raw)
                and component['coordinates'] == {'x': -9999, 'y': -9999}
                and component['is_native_invalid_sentinel'] is False,
                f'{name} forecast does not match the admitted raw building value')
        modifier = one(analysis['modifier_values'],
                       lambda record: record['building_call_id'] == component['id']
                       and record['own_building_callsite'] is True,
                       f'{name} own ModifierValue')
        require(modifier['matches'] is True
                and component['own_modifier_call_ids'] == [modifier['id']]
                and component['own_modifier_q8'] == modifier['value_q8'],
                f'{name} ModifierValue does not reconcile')

        root_ids = (WIND_ROOT,) if name == WIND else WATER_ROOTS
        removed = 0
        for root_id in root_ids:
            root = one(analysis['modifier_calls'],
                       lambda record: record['building_call_id'] == component['id']
                       and record['modifier'] == root_id and record['own_building_root'] is True,
                       f'{name} consumed {root_id} root')
            credit = root['restored_q8']
            require(root['id'] in modifier['direct_analyzers']
                    and root['parent_id'] == modifier['id']
                    and (root['player'], root['city'], root['building_type']) == (player, city, name)
                    and root['source_found'] is True and root['consumed_by_modifier_value'] is True
                    and root['accepted'] == 1 and positive_q8(credit),
                    f'{name} {root_id} credit does not reconcile')
            if name == WIND:
                require(root['source_effect'] == 'EFFECT_ATTACH_MODIFIER'
                        and root['source_collection'] == 'COLLECTION_CITY_DISTRICTS'
                        and root['arguments'] == {'ModifierId': WIND_CHILD},
                        'Unexpected Wind hill attachment')
                children = [record for record in analysis['modifier_calls']
                            if record['parent_id'] == root['id']]
                require(bool(children) and all(
                    record['modifier'] == WIND_CHILD
                    and record['source_effect'] == 'EFFECT_ADJUST_DISTRICT_BASE_YIELD_CHANGE'
                    and record['arguments'] == {'Amount': '1', 'YieldType': 'YIELD_PRODUCTION'}
                    for record in children), 'Unexpected Wind hill child')
                final_child = max(children, key=lambda record: record['leave_sequence'])
                require(final_child['accepted'] == 1 and final_child['restored_q8'] == credit,
                        'Wind hill root does not match the surviving child result')
            else:
                require(root['source_effect'] == 'EFFECT_ADJUST_BUILDING_YIELD_CHANGE'
                        and root['source_collection'] == 'COLLECTION_OWNER'
                        and root['arguments'] == {'BuildingType': WATER,
                                                  'YieldType': WATER_ROOTS[root_id], 'Amount': '1'},
                        f'Unexpected Water recipient in {name} {root_id}')
            removed += credit
            receipts.append({'building': name, 'building_call_id': component['id'],
                             'modifier_call_id': modifier['id'], 'root_call_id': root['id'],
                             'modifier': root_id, 'credit_q8': credit})

        adjusted = raw - removed
        # Civ contributes zero for a nonpositive raw building forecast. The
        # remaining negative Wind value therefore contributes zero here.
        replacement = max(0, adjusted)
        results.append({'building': name, 'raw_q8': raw, 'removed_root_credit_q8': removed,
                        'corrected_raw_q8': adjusted, 'replacement_q8': replacement,
                        'delta_q8': replacement - raw})

    corrected_uplift = sum(record['replacement_q8'] for record in results)
    corrected = before + corrected_uplift
    require(0 < corrected < native, 'Correction must lower this score without invalidating the row')
    return {'player': player, 'city': city, 'plot': plot, 'row': row['row'],
            'district': BAKERS, 'district_index': district['index'], 'calculation_id': calc['id'],
            'before_aggregation_q8': before, 'native_building_uplift_q8': raw_total,
            'corrected_building_uplift_q8': corrected_uplift,
            'expected_native_q8': native, 'corrected_q8': corrected,
            'delta_q8': corrected - native, 'buildings': results, 'root_receipts': receipts}
