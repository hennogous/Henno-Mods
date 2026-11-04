"""Attribute a frozen read-only Bakers observation; never import game tooling.

The original80 world is a prior treated world. Recalculation without its old
score writer is not reproduction of the unrecorded historical86/89 totals.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

BITS = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512)
INVALID = -2559744
QUARTER = 'DISTRICT_CSC_BAKERS_QUARTER'


def expand_database(world):
    """Decode the lossless world.lua schema, preserving absent versus zero."""
    strings = world.get('databaseStrings', [])

    def cell(value):
        if isinstance(value, dict) and set(value) == {'s'}:
            index = value['s']
            if not isinstance(index, int) or not 1 <= index <= len(strings):
                raise ValueError('Invalid database string reference')
            return strings[index - 1]
        return value

    tables = {}
    for name, table in world['relevantDB'].items():
        if isinstance(table, list):
            tables[name] = table
            continue
        columns = table['columns']
        if len(columns) != len(set(columns)):
            raise ValueError('Duplicate compact columns')
        rows = []
        for row in table['rows']:
            if len(row) != len(columns):
                raise ValueError('Compact row width mismatch')
            rows.append({key: cell(value) for key, value in zip(columns, row)
                         if value != table.get('absent', 'ABSENT')})
        tables[name] = rows
    return tables


def identity(record):
    who = record['entry']['identity']
    return who['player'], who['city']


def interval(record):
    return record['entrySequence'], record['leave']['sequence']


def contained(child, parent):
    a, b = interval(child)
    x, y = interval(parent)
    return child['thread'] == parent['thread'] and x < a < b < y


def bit_wrapper_contract(db, building):
    """Recover the source bridge behind a counted bit, not from Amount alone."""
    modifiers = {row['ModifierId']: row for row in db.get('modifiers', [])}
    args = {}
    for row in db.get('modifierArguments', []):
        args.setdefault(row['ModifierId'], {})[row['Name']] = row['Value']
    rows = []
    for root in db.get('buildingModifiers', []):
        if root['building'] != building:
            continue
        outer = modifiers.get(root['modifier'], {})
        child_id = args.get(root['modifier'], {}).get('ModifierId')
        child = modifiers.get(child_id, {})
        child_args = args.get(child_id, {})
        if not (outer.get('CollectionType') == 'COLLECTION_PLAYER_DISTRICTS'
                and outer.get('EffectType') == 'EFFECT_ATTACH_MODIFIER'
                and child.get('CollectionType') == 'COLLECTION_OWNER'
                and child.get('EffectType') == 'EFFECT_ADJUST_DISTRICT_BASE_YIELD_CHANGE'):
            continue
        try:
            amount = int(child_args['Amount'])
        except (KeyError, TypeError, ValueError):
            continue
        if amount not in BITS or child_args.get('YieldType') != 'YIELD_PRODUCTION':
            continue
        rows.append({'root': root['modifier'], 'child': child_id,
                     'amount': amount, 'yield': child_args['YieldType'],
                     'outer_owner_gate': outer.get('OwnerRequirementSetId'),
                     'outer_subject_gate': outer.get('SubjectRequirementSetId'),
                     'child_owner_gate': child.get('OwnerRequirementSetId'),
                     'child_subject_gate': child.get('SubjectRequirementSetId')})
    amounts = sorted(row['amount'] for row in rows)
    exact = amounts == list(BITS) and all(
        row['outer_owner_gate'] is None and row['outer_subject_gate'] is None
        and row['child_owner_gate'] is not None and row['child_subject_gate'] is None
        for row in rows)
    return {'exact_ten_bit_source_topology': exact, 'wrappers': rows,
            'encoded_capacity': sum(row['amount'] for row in rows)}


def build_component_rows(records, db, errors):
    values = [r for r in records if r['kind'] == 'BuildingValue']
    sums = [r for r in records if r['kind'] == 'ModifierValue']
    effects = [r for r in records if r['kind'] == 'BaseYield']
    rows = []
    for building in values:
        direct_sums = [r for r in sums if r.get('parentId') == building['id']
                       and contained(r, building)]
        bit_contract = bit_wrapper_contract(db, building['entry']['buildingType'])
        modifier_rows = []
        for modifier in direct_sums:
            children = [r for r in effects if r.get('parentId') == building['id']
                        and contained(r, modifier)]
            grouped = {}
            for effect in children:
                if effect['entry']['amount'] not in BITS:
                    continue
                key = (effect['entry']['amount'], effect['entry']['effectYieldIndex'])
                grouped.setdefault(key, []).append(effect)
            bit_rows = []
            for (amount, yield_index), group in sorted(grouped.items()):
                group.sort(key=lambda r: r['entrySequence'])
                deltas = [r['leave']['accumulatorDelta'] for r in group]
                after = [r['leave']['analysis']['accumulator'] for r in group]
                bit_rows.append({'amount': amount, 'native_yield_index': yield_index,
                                 'calls': len(group), 'last_effect_id': group[-1]['id'],
                                 'district_context_pointers': sorted(set(
                                     r['entry']['analysis']['districtPointer'] for r in group)),
                                 'all_have_actual_district_context': all(
                                     r['entry']['analysis']['districtPointer'] != '0x0' for r in group),
                                 'delta_min': min(deltas), 'delta_max': max(deltas),
                                 'last_accumulator_whole_utility': after[-1],
                                 'last_accumulator_q8': after[-1] * 256,
                                 'constant_delta_across_contexts': min(deltas) == max(deltas)})
            exact_bits = (bit_contract['exact_ten_bit_source_topology']
                          and len(bit_rows) == 10
                          and [r['amount'] for r in bit_rows] == list(BITS)
                          and len({r['native_yield_index'] for r in bit_rows}) == 1
                          and all(r['all_have_actual_district_context'] for r in bit_rows))
            # AttachModifier assigns its nested result on each outer district;
            # therefore the last child for each source wrapper is the result
            # surviving that wrapper. Summing every district callback is wrong.
            bits_q8 = sum(row['last_accumulator_q8'] for row in bit_rows) if exact_bits else None
            value_q8 = modifier['leave'].get('valueQ8')
            modifier_rows.append({'id': modifier['id'], 'modifier_count': modifier['entry']['modifierCount'],
                                  'value_q8': value_q8, 'base_effect_calls': len(children),
                                  'bit_rows': bit_rows, 'exact_ten_bit_path_observed': exact_bits,
                                  'bits_surviving_assignment_q8': bits_q8,
                                  'remaining_modifier_value_q8': value_q8 - bits_q8 if bits_q8 is not None else None,
                                  'all_bit_context_deltas_constant': exact_bits and all(
                                      r['constant_delta_across_contexts'] for r in bit_rows)})
        total_modifier = sum(r['value_q8'] for r in modifier_rows)
        value_q8 = building['leave'].get('valueQ8')
        rows.append({'id': building['id'], 'player': identity(building)[0],
                     'city': identity(building)[1], 'building': building['entry']['building'],
                     'building_type': building['entry']['buildingType'], 'ready': building['entry']['ready'],
                     'horizon': building['entry']['horizon'], 'discount_q8': building['entry']['discountQ8'],
                     'coordinates': building['entry']['coordinates'], 'value_q8': value_q8,
                     'modifier_total_q8': total_modifier,
                     'non_modifier_remainder_q8': value_q8 - total_modifier,
                     'modifier_sums': modifier_rows, 'source_bit_contract': bit_contract,
                     'entry_sequence': building['entrySequence'], 'leave_sequence': building['leave']['sequence']})
    # Every nested sum/effect must belong to a captured paired building interval.
    for child in sums + effects:
        parents = [r for r in values if r['id'] == child.get('parentId') and contained(child, r)]
        if len(parents) != 1:
            errors.append('Missing/ambiguous building parent for record ' + str(child['id']))
    return rows


def aggregation_rows(records, world, db, components, warnings):
    family = {row['Index']: row for row in db['buildings']}
    family_by_type = {row['BuildingType']: row for row in db['buildings']}
    target_world = {(row['player'], row['city']): row for row in world['targets']}
    out = []
    for record in records:
        if record['kind'] != 'CalculateDistrictValues':
            continue
        source = target_world[identity(record)]
        before, after = record['entry']['cache'], record['leave'].get('cache', {})
        item = {'id': record['id'], 'player': identity(record)[0], 'city': identity(record)[1],
                'world_gate_reference_turn': world['turn'],
                'gate_facts_are_not_a_mid_callback_snapshot': True,
                'source_city_has_bakers': source.get('hasBakers'), 'buildings': [], 'rows': []}
        if before.get('status') != 'observed' or after.get('status') != 'observed':
            item['status'] = 'cache_unobserved'
            out.append(item)
            continue
        present = {row['type']: row['present'] for row in source['buildings']}
        raw_values = {row['index']: row['value'] for row in before['rawBuildingQ8']}
        gate_unknown = source.get('hasBakers') is not False
        expected_sum = 0
        for index, definition in sorted(family.items()):
            name = definition['BuildingType']
            value = raw_values.get(index)
            reasons = []
            if value is None:
                reasons.append('raw_input_unobserved')
                gate_unknown = True
            elif value <= 0:
                reasons.append('nonpositive_raw_value')
            if definition.get('MustPurchase') in (1, True):
                reasons.append('must_purchase')
            if definition.get('PrereqDistrict') != QUARTER:
                reasons.append('not_bakers_prerequisite')
            for exclusion in db.get('mutualExclusions', []):
                if exclusion['building'] != name:
                    continue
                other = family_by_type.get(exclusion['excluded'])
                other_index = exclusion.get('excludedIndex', other['Index'] if other else None)
                if present.get(exclusion['excluded']) is True:
                    reasons.append('excluded_building_present:' + exclusion['excluded'])
                elif other_index is None:
                    reasons.append('excluded_index_unknown')
                    gate_unknown = True
                elif other_index < index:
                    reasons.append('lower_index_mutual_canonical:' + exclusion['excluded'])
            admitted = not reasons and source.get('hasBakers') is False
            if admitted:
                expected_sum += value
            preceding = [row for row in components if (row['player'], row['city']) == identity(record)
                         and row['building'] == index and row['leave_sequence'] < record['entrySequence']]
            latest = max(preceding, key=lambda row: row['leave_sequence']) if preceding else None
            item['buildings'].append({'index': index, 'type': name, 'raw_q8': value,
                                      'admitted_by_source_gates': admitted,
                                      'excluded_reasons': reasons,
                                      'latest_observed_value_call_id': latest['id'] if latest else None,
                                      'latest_value_return_matches_raw': latest['value_q8'] == value if latest else None})
        item['derived_building_sum_q8'] = expected_sum if not gate_unknown else None
        before_rows = before['districtRows']
        after_rows = after['districtRows']
        geometry_matches = len(before_rows) == len(after_rows) and all(
            (a['row'], a['plot']) == (b['row'], b['plot']) for a, b in zip(before_rows, after_rows))
        if not geometry_matches:
            item['status'] = 'row_identity_changed'
            out.append(item)
            continue
        positive, exact, unchanged = 0, 0, 0
        for a, b in zip(before_rows, after_rows):
            expected = a['value']
            if expected_sum and a['value'] > 0:
                expected = expected_sum if a['row'] == 0 else a['value'] + expected_sum
                positive += 1
            observed = b['value']
            match = expected == observed
            exact += int(match)
            unchanged += int(a['value'] == observed)
            item['rows'].append({'row': a['row'], 'plot': a['plot'], 'before_q8': a['value'],
                                 'after_q8': observed, 'observed_delta_q8': observed - a['value'],
                                 'expected_after_q8': expected if not gate_unknown else None,
                                 'matches_derived_sum': match if not gate_unknown else None})
        item['positive_rows_testing_uplift'] = positive
        item['all_rows_match_derived_sum'] = not gate_unknown and exact == len(before_rows)
        item['all_observed_row_pointers_unchanged'] = unchanged == len(before_rows)
        if item['all_rows_match_derived_sum'] and positive:
            item['status'] = 'exact_conditional_aggregation_match'
        elif positive and item['all_observed_row_pointers_unchanged']:
            item['status'] = 'mutable_district_matrix_binding_unobserved'
            warnings.append('Calculation ' + str(record['id']) + ': row+0x20 stayed unchanged; '
                            'do not infer no uplift without observing the mutable +0x508 map backing.')
        else:
            item['status'] = 'aggregation_mismatch_or_inert'
        out.append(item)
    return out


def analyze(trace, world):
    errors, warnings = [], []
    if trace.get('profile') != 'bakers-components-v1' or world.get('profile') != 'bakers-components-v1':
        raise ValueError('Wrong profile')
    if trace.get('read_only') is not True:
        errors.append('Trace is not explicitly read-only')
    if trace.get('config') != world.get('observerConfig') or trace.get('config') is None:
        errors.append('Trace/world immutable mappings disagree')
    if trace.get('stats', {}).get('errors') != 0 or trace.get('faults'):
        errors.append('Observer faults present')
    if trace.get('pendingPairs') != 0 or trace.get('pendingFrames') != 0:
        errors.append('Native callbacks/pairs remain in flight')
    if trace.get('frozen') is not True or trace.get('stopReason'):
        errors.append('Window not cleanly frozen or budget-limited')
    records = trace.get('records', [])
    if not records:
        errors.append('No records')
    if trace.get('stats', {}).get('completedPairs') != len(records) or trace.get('stats', {}).get('acceptedPairs') != len(records):
        errors.append('Pair counts disagree with completed records')
    ids = [r['id'] for r in records]
    if len(ids) != len(set(ids)):
        errors.append('Duplicate record IDs')
    for row in records:
        if row['kind'] not in ('BuildingValue', 'ModifierValue', 'BaseYield', 'CalculateDistrictValues'):
            errors.append('Unknown record kind ' + str(row['kind']))
        if row['leave'].get('incompleteReason') or row['leave'].get('captureMayBeIncomplete'):
            errors.append('Incomplete record ' + str(row['id']))
        if interval(row)[1] <= interval(row)[0]:
            errors.append('Invalid interval ' + str(row['id']))
    # Preserve faulty observations but refuse component arithmetic on missing data.
    if errors:
        return {'schema': 1, 'ok': False, 'errors': errors, 'warnings': warnings,
                'record_count': len(records), 'recalculation_not_historical_reproduction': True}
    db = expand_database(world)
    components = build_component_rows(records, db, errors)
    aggregates = aggregation_rows(records, world, db, components, warnings)
    mills = [row for row in components if row['building_type'].endswith(('_WIND_MILL', '_WATER_MILL'))]
    bit_sums = [m for row in mills for m in row['modifier_sums'] if m['exact_ten_bit_path_observed']]
    actual_bits = []
    for district in world.get('ownerDistricts', []):
        for rule in district['plot'].get('millProperties', []):
            actual_bits.append({'player': district['player'], 'plot': district['plot']['index'],
                                'rule_index': rule['ruleIndex'], 'enabled_amount': rule['amountSum'],
                                'bit512_property': rule['bitValues'][-1]})
    return {'schema': 1, 'ok': not errors, 'errors': errors, 'warnings': warnings,
            'record_count': len(records), 'source_world_turn': world['turn'],
            'recalculation_not_historical_reproduction': True,
            'single_immutable_observer_window': True,
            'native_analysis_generation_api_observed': False,
            'gameplay_yield_change_or_economic_benefit_proven': False,
            'exact_ten_bit_modifier_sums_observed': len(bit_sums),
            'all_exact_bit_sums_equal_entire_modifier_value': bool(bit_sums) and all(
                row['remaining_modifier_value_q8'] == 0 for row in bit_sums),
            'all_actual_owner_districts_have_bit512_disabled': bool(actual_bits) and all(
                row['bit512_property'] != 1 for row in actual_bits),
            'actual_district_property_bits': actual_bits,
            'building_components': components, 'district_aggregations': aggregates,
            'interpretation_limits': [
                'Source-world eligibility facts were read before the native interval, not inside each callback.',
                'Native accumulator units are whole utility; ModifierValue restores Q8. They are not raw yields.',
                'A non-modifier remainder is unitemized native value, not automatically correct CSC benefit.',
                'Exact family inputs do not prove mutable district matrix writes when only row+0x20 was read.',
                'No historical86/89 component reconstruction, caused site switch or economic benefit follows.']}


def markdown(result):
    lines = ['# Bakers forecast component observation', '',
             f"Read-only collection integrity: **{'pass' if result['ok'] else 'fail'}**. "
             f"Completed records: {result['record_count']}.", '',
             'This is a recalculation in the archived turn80 world, without its old score writer; '
             'it does not reconstruct the missing historical86/89 components.', '']
    for error in result['errors']:
        lines.append('- Error: ' + error)
    for warning in result['warnings']:
        lines.append('- Scope: ' + warning)
    if not result['ok']:
        return '\n'.join(lines) + '\n'
    lines += ['', '| Player/city | Building | Native Q8 | Modifier Q8 | Other native Q8 |',
              '| --- | --- | ---: | ---: | ---: |']
    for row in result['building_components']:
        lines.append(f"| {row['player']}/{row['city']} | {row['building_type']} | "
                     f"{row['value_q8']} | {row['modifier_total_q8']} | {row['non_modifier_remainder_q8']} |")
    lines += ['', '## Generated binary modifiers', '',
              f"Exact ten-bit modifier sums observed: **{result['exact_ten_bit_modifier_sums_observed']}**. "
              f"Their last-per-wrapper results explain each entire observed modifier sum: "
              f"**{result['all_exact_bit_sums_equal_entire_modifier_value']}**.", '',
              'Callback amounts are not all added across player districts: the nested attach handler '
              'assigns its child result. The analyzer uses the last observed result for each distinct bit.', '',
              '## District aggregation', '',
              '| Calculation | Player/city | Derived building Q8 | Observed status |',
              '| --- | --- | ---: | --- |']
    for row in result['district_aggregations']:
        lines.append(f"| {row['id']} | {row['player']}/{row['city']} | "
                     f"{row.get('derived_building_sum_q8')} | {row['status']} |")
    lines += ['', '## Limits', ''] + ['- ' + item for item in result['interpretation_limits']]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trace', type=Path, required=True)
    parser.add_argument('--world', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    trace = json.loads(a.trace.read_text(encoding='utf-8-sig'))
    world = json.loads(a.world.read_text(encoding='utf-8-sig'))
    result = analyze(trace, world)
    result['inputs'] = [{'path': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                        for path in (a.trace, a.world)]
    a.output.mkdir(parents=True, exist_ok=True)
    (a.output / 'analysis.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    (a.output / 'summary.md').write_text(markdown(result), encoding='utf-8')
    print(json.dumps({key: result[key] for key in ('ok', 'record_count', 'errors', 'warnings')}))
    if not result['ok']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
