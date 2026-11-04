"""Finite offline ledger checks; no game, native libraries or browser imports."""
import copy
import unittest

from analyze import analyze, expand_database, BITS, QUARTER


def fixture():
    names = ['BUILDING_CSC_BAKERS_' + x for x in
             ('RIVER_ACCESS', 'NO_RIVER_ACCESS', 'WIND_MILL', 'WATER_MILL', 'BAKERY', 'CAFE')]
    buildings = [{'Index': i, 'BuildingType': name, 'MustPurchase': i < 2,
                  'PrereqDistrict': QUARTER} for i, name in enumerate(names)]
    db = {'buildings': buildings, 'mutualExclusions': [
        {'building': names[2], 'excluded': names[3], 'excludedIndex': 3},
        {'building': names[3], 'excluded': names[2], 'excludedIndex': 2}],
        'buildingModifiers': [], 'modifiers': [], 'modifierArguments': []}
    for bit in BITS:
        outer, child = 'OUTER_' + str(bit), 'CHILD_' + str(bit)
        db['buildingModifiers'].append({'building': names[2], 'modifier': outer})
        db['modifiers'] += [
            {'ModifierId': outer, 'CollectionType': 'COLLECTION_PLAYER_DISTRICTS', 'EffectType': 'EFFECT_ATTACH_MODIFIER'},
            {'ModifierId': child, 'CollectionType': 'COLLECTION_OWNER', 'EffectType': 'EFFECT_ADJUST_DISTRICT_BASE_YIELD_CHANGE',
             'OwnerRequirementSetId': 'BIT_' + str(bit)}]
        db['modifierArguments'] += [
            {'ModifierId': outer, 'Name': 'ModifierId', 'Value': child},
            {'ModifierId': child, 'Name': 'Amount', 'Value': str(bit)},
            {'ModifierId': child, 'Name': 'YieldType', 'Value': 'YIELD_PRODUCTION'}]
    who = {'player': 5, 'city': 65536, 'pointer': '0x10000'}
    raw = [100, 200, 1000, 2000, 300, 400]
    cache = {'status': 'observed', 'rawBuildingQ8': [{'index': i, 'type': n, 'value': raw[i]} for i, n in enumerate(names)],
             'districtRows': [{'row': 0, 'plot': 100, 'value': 1},
                              {'row': 1, 'plot': 1429, 'value': 1207},
                              {'row': 2, 'plot': 1430, 'value': 0},
                              {'row': 3, 'plot': 1431, 'value': -2559744}]}
    after = copy.deepcopy(cache)
    after['districtRows'][0]['value'] = 1700
    after['districtRows'][1]['value'] += 1700
    records = []
    counter = 0

    def seq():
        nonlocal counter
        counter += 1
        return counter

    root = {'kind': 'BuildingValue', 'id': 1, 'thread': 1, 'entrySequence': seq(),
            'entry': {'identity': who, 'building': 2, 'buildingType': names[2], 'ready': 10,
                      'horizon': 60, 'discountQ8': 20, 'coordinates': {'x': -9999, 'y': -9999}}}
    modifier = {'kind': 'ModifierValue', 'id': 2, 'thread': 1, 'parentId': 1,
                'entrySequence': seq(), 'entry': {'identity': who, 'modifierCount': 10}}
    # Two player-district callbacks per bit; assignment retains the last, not sum.
    for bit in BITS:
        for district in ('0x20000', '0x30000'):
            records.append({'kind': 'BaseYield', 'id': len(records) + 3, 'thread': 1,
                            'parentId': 1, 'entrySequence': seq(),
                            'entry': {'identity': who, 'amount': bit, 'effectYieldIndex': 1,
                                      'analysis': {'districtPointer': district}},
                            'leave': {'sequence': seq(), 'accumulatorDelta': bit * 2,
                                      'analysis': {'accumulator': bit * 2}}})
    modifier['leave'] = {'sequence': seq(), 'valueQ8': 1023 * 2 * 256}
    root['leave'] = {'sequence': seq(), 'valueQ8': 1023 * 2 * 256 - 512}
    records += [modifier, root]
    records.append({'kind': 'CalculateDistrictValues', 'id': 100, 'thread': 1,
                    'entrySequence': seq(), 'entry': {'identity': who, 'cache': cache},
                    'leave': {'sequence': seq(), 'cache': after}})
    source = {'profile': 'bakers-components-v1', 'turn': 80, 'relevantDB': db,
              'targets': [{'player': 5, 'city': 65536, 'hasBakers': False,
                           'buildings': [{'type': n, 'present': False} for n in names]}],
              'ownerDistricts': [{'player': 5, 'plot': {'index': 100, 'millProperties': [
                  {'ruleIndex': 1, 'amountSum': 0, 'bitValues': ['ABSENT'] * 10}]}}]}
    trace = {'profile': 'bakers-components-v1', 'read_only': True, 'frozen': True,
             'pendingPairs': 0, 'pendingFrames': 0, 'stopReason': None,
             'faults': [], 'records': records,
             'stats': {'errors': 0, 'acceptedPairs': len(records), 'completedPairs': len(records)}}
    trace['config'] = {'profile': 'bakers-components-v1', 'fixture': True}
    source['observerConfig'] = copy.deepcopy(trace['config'])
    return trace, source


class LedgerTests(unittest.TestCase):
    def test_nested_bit_sum_uses_assignment_not_district_multiplication(self):
        trace, world = fixture()
        result = analyze(trace, world)
        self.assertTrue(result['ok'])
        self.assertEqual(result['exact_ten_bit_modifier_sums_observed'], 1)
        row = result['building_components'][0]
        self.assertEqual(row['modifier_total_q8'], 523776)
        self.assertEqual(row['non_modifier_remainder_q8'], -512)
        self.assertEqual(row['modifier_sums'][0]['bits_surviving_assignment_q8'], 523776)
        self.assertTrue(result['all_exact_bit_sums_equal_entire_modifier_value'])
        self.assertEqual(row['modifier_sums'][0]['base_effect_calls'], 20)
        self.assertTrue(result['all_actual_owner_districts_have_bit512_disabled'])

    def test_native_gate_ledger_excludes_hidden_and_higher_index_mill(self):
        trace, world = fixture()
        row = analyze(trace, world)['district_aggregations'][0]
        self.assertEqual(row['derived_building_sum_q8'], 1700)
        self.assertEqual(row['status'], 'exact_conditional_aggregation_match')
        self.assertTrue(row['all_rows_match_derived_sum'])
        self.assertEqual(row['buildings'][0]['excluded_reasons'], ['must_purchase'])
        self.assertIn('lower_index_mutual_canonical:BUILDING_CSC_BAKERS_WIND_MILL', row['buildings'][3]['excluded_reasons'])
        self.assertEqual([x['after_q8'] for x in row['rows']], [1700, 2907, 0, -2559744])

    def test_unchanged_raw_district_pointer_does_not_claim_no_uplift(self):
        trace, world = fixture()
        record = next(x for x in trace['records'] if x['kind'] == 'CalculateDistrictValues')
        record['leave']['cache'] = copy.deepcopy(record['entry']['cache'])
        result = analyze(trace, world)
        self.assertTrue(result['ok'])
        self.assertEqual(result['district_aggregations'][0]['status'], 'mutable_district_matrix_binding_unobserved')
        self.assertTrue(result['warnings'])

    def test_faults_pending_and_budget_abort_component_claims(self):
        for changes in ({'stopReason': 'pair_budget'}, {'pendingFrames': 1}, {'frozen': False}):
            trace, world = fixture()
            trace.update(changes)
            result = analyze(trace, world)
            self.assertFalse(result['ok'])
            self.assertNotIn('building_components', result)

    def test_missing_bit_or_source_gate_cannot_be_exact_path(self):
        trace, world = fixture()
        for mod in world['relevantDB']['modifiers']:
            if mod['ModifierId'] == 'CHILD_512':
                mod['SubjectRequirementSetId'] = 'AN_EXTRA_GATE'
        result = analyze(trace, world)
        self.assertEqual(result['exact_ten_bit_modifier_sums_observed'], 0)
        self.assertIsNone(result['building_components'][0]['modifier_sums'][0]['bits_surviving_assignment_q8'])

    def test_compact_metadata_preserves_zero_and_validates_references(self):
        world = {'databaseStrings': ['LONG_BUILDING_IDENTIFIER'], 'relevantDB': {
            'buildings': {'columns': ['BuildingType', 'MustPurchase', 'Unused'],
                          'rows': [[{'s': 1}, 0, 'ABSENT']], 'absent': 'ABSENT'}}}
        row = expand_database(world)['buildings'][0]
        self.assertEqual(row, {'BuildingType': 'LONG_BUILDING_IDENTIFIER', 'MustPurchase': 0})
        world['relevantDB']['buildings']['rows'][0][0] = {'s': 2}
        with self.assertRaises(ValueError):
            expand_database(world)

    def test_orphan_component_is_not_accepted_as_attributed(self):
        trace, world = fixture()
        trace['records'][0]['parentId'] = 999
        result = analyze(trace, world)
        self.assertFalse(result['ok'])
        self.assertTrue(any('parent' in x for x in result['errors']))

    def test_cross_mapping_mix_is_rejected_before_component_claim(self):
        trace, world = fixture()
        world['observerConfig']['fixture'] = False
        result = analyze(trace, world)
        self.assertFalse(result['ok'])
        self.assertTrue(any('mappings' in x for x in result['errors']))


if __name__ == '__main__':
    unittest.main()
