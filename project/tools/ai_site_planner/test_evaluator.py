import copy
import json
import math
import unittest
from pathlib import Path

from evaluator import evaluate, review

PACKET = json.loads((Path(__file__).parent/'fixtures/captured_sites.json').read_text(encoding='utf-8'))
RULES = PACKET['rules']


def site():
    return dict(id='test:p3:c1:TAILORS:10', group='test:p3:c1:TAILORS', name='Controlled case',
        original_human=False, identity=dict(world='test', player=3, city=1, plot=10, quarter='TAILORS', turn=1),
        quarter=dict(exists=True, complete=True, pillaged=False), city=dict(production=20, population=10),
        land=dict(legal=True, district_cost=30, reservation=None), existing_buildings={'2': True},
        river_edges=0, materials=[], customers=[], service_unlocks={}, future_footprints=[])


def material(plot=11, *, base=True, spec=False, working=True, worked=True):
    return dict(plot=plot, resource='TEST_RESOURCE', base=base, specialty=spec, working=working,
                worked=worked, owned=True, revealed=True, district_free=True, intensity=1)


def customer(kind='DISTRICT_HOLY_SITE', plot=12, population=20, city=2):
    building = {'DISTRICT_HOLY_SITE': 'BUILDING_TEMPLE', 'DISTRICT_COMMERCIAL_HUB': 'BUILDING_MARKET',
                'DISTRICT_THEATER': 'BUILDING_AMPHITHEATER', 'DISTRICT_HARBOR': 'BUILDING_LIGHTHOUSE'}[kind]
    return dict(key=f'3:{city}:{plot}:{kind}', owner=3, city=city, plot=plot, district=kind,
                population=population, functioning=True, district_functioning=True, building=building)


def branch(s, cost=100):
    c = customer('DISTRICT_HARBOR', plot=20)
    c.update(ready_turn=10, cost=cost, maintenance=1, conflict=False, ordinary_yields={'gold': 3})
    s['future_footprints'] = [dict(plot=20, native_potential={'DISTRICT_HARBOR': True})]
    return c


def component(result, yield_type, prefix):
    return sum(row['value_per_turn'] for row in result['ledger'][yield_type] if row['component'].startswith(prefix))


class MechanicsTests(unittest.TestCase):
    def test_ordinary_temple_sales_work_without_base(self):
        s = site(); s['existing_buildings']['3'] = True; s['customers'] = [customer()]
        result = evaluate(s, [2, 3], RULES)
        self.assertAlmostEqual(component(result, 'production', 'stage3.seller'), 2.1)
        self.assertAlmostEqual(component(result, 'gold', 'stage3.seller'), 2.1)
        self.assertEqual(result['services'][1]['state'], 'missing_path')

    def test_same_city_market_and_temple_are_distinct_transactions(self):
        s = site(); s['existing_buildings']['3'] = True
        s['customers'] = [customer(city=2), customer('DISTRICT_COMMERCIAL_HUB', 13, city=2)]
        result = evaluate(s, [2, 3], RULES)
        self.assertAlmostEqual(component(result, 'production', 'stage3.seller'), 4.2)

    def test_stage4_rounds_each_customer_population_before_summing(self):
        s = site(); s['existing_buildings']['4'] = True
        s['customers'] = [customer('DISTRICT_THEATER', 12, 4, 2), customer('DISTRICT_THEATER', 13, 4, 3)]
        result = evaluate(s, [2, 4], RULES)
        self.assertEqual(component(result, 'production', 'stage4.seller'), 0)

    def test_missing_customer_building_gets_flat_adjacency_only(self):
        s = site(); c = customer(); c.update(building=None, functioning=False); s['customers'] = [c]
        result = evaluate(s, [2, 3], RULES)
        self.assertEqual(component(result, 'gold', 'district.customer'), 1)
        self.assertEqual(component(result, 'production', 'stage3.seller'), 0)
        self.assertEqual(component(result, 'culture', 'customer.reciprocal'), 1)

    def test_incomplete_customer_district_gets_no_realised_reciprocal_yield(self):
        s = site(); c = customer(); c.update(district_functioning=False, functioning=False)
        s['customers'] = [c]; result = evaluate(s, [2], RULES)
        self.assertEqual(component(result, 'gold', 'district.customer'), 1)
        self.assertEqual(component(result, 'culture', 'customer.reciprocal'), 0)

    def test_unworked_material_supplies_workshop_but_has_no_realised_tile_income(self):
        s = site(); s['materials'] = [material(worked=False)]
        result = evaluate(s, [2], RULES)
        self.assertEqual(component(result, 'culture', 'workshop.material'), 1)
        self.assertEqual(component(result, 'production', 'material.workshop'), 0)

    def test_unknown_working_citizen_is_not_assumed(self):
        s = site(); s['materials'] = [material(worked=None)]
        result = evaluate(s, [2], RULES)
        self.assertEqual(component(result, 'production', 'material.workshop'), 0)
        self.assertTrue(any('Citizen working' in u for u in result['unknowns']))

    def test_unimproved_resource_gets_flat_adjacency_without_producer_supply(self):
        s = site(); s['materials'] = [material(working=False)]
        result = evaluate(s, [2], RULES)
        self.assertEqual(component(result, 'production', 'district.materials'), 1)
        self.assertEqual(component(result, 'culture', 'workshop.material'), 0)

    def test_industry_uses_twofold_material_exchange(self):
        s = site(); m = material(); m['intensity'] = 2; s['materials'] = [m]
        result = evaluate(s, [2], RULES)
        self.assertEqual(component(result, 'culture', 'workshop.material'), 2)

    def test_one_river_edge_has_no_flat_production_but_two_do(self):
        s = site(); s['river_edges'] = 1; first = evaluate(s, [2], RULES)
        s['river_edges'] = 2; second = evaluate(s, [2], RULES)
        self.assertEqual(component(first, 'production', 'district.materials'), 0)
        self.assertEqual(component(second, 'production', 'district.materials'), 1)

    def test_foreign_customer_has_no_empire_credit(self):
        s = site(); c = customer(); c['owner'] = 4; s['customers'] = [c]
        self.assertEqual(component(evaluate(s, [2, 3], RULES), 'gold', 'district.customer'), 0)

    def test_fashion_house_does_not_require_tailor(self):
        s = site(); result = evaluate(s, [2, 4], RULES)
        self.assertNotIn('BUILDING_CSC_TAILORS_TAILOR', [r['item'] for r in result['schedule']])

    def test_base_with_customer_can_beat_both_without_customer(self):
        a = site(); a['materials'] = [material()]; a['customers'] = [customer()]
        b = copy.deepcopy(a); b['customers'] = []; b['materials'].append(material(13, base=False, spec=True))
        self.assertGreater(evaluate(a, [2, 3], RULES)['review_utility'], evaluate(b, [2, 3], RULES)['review_utility'])


class InvestmentTests(unittest.TestCase):
    def test_retain_existing_state_is_zero_incremental_value(self):
        s = site(); result = review(s, RULES)
        retained = next(r for r in result['plans'] if r['plan'] == [2])
        self.assertEqual(retained['review_utility'], 0)
        self.assertEqual(retained['construction_cost'], 0)

    def test_future_customer_cost_is_not_cancelled_by_existing_baseline(self):
        s = site(); future = branch(s, 100)
        first = next(r for r in review(s, RULES, future=future)['plans'] if r['plan'] == [2])
        future['cost'] = 150
        second = next(r for r in review(s, RULES, future=future)['plans'] if r['plan'] == [2])
        self.assertAlmostEqual(first['review_utility']-second['review_utility'], 50)

    def test_future_customer_is_conditional_and_does_not_mutate_capture(self):
        s = site(); future = branch(s); before = copy.deepcopy(s)
        result = evaluate(s, [2], RULES, future=future)
        self.assertEqual(s, before)
        self.assertTrue(result['conditional_future'])
        self.assertFalse(result['deployable'])

    def test_future_customer_needs_recorded_plot_potential(self):
        s = site(); future = branch(s); s['future_footprints'] = []
        with self.assertRaises(ValueError): evaluate(s, [2], RULES, future=future)

    def test_positive_conditional_cashflow_does_not_hide_missing_base_goal(self):
        s = site(); s['quarter']['exists'] = False; s['existing_buildings'] = {}
        future = branch(s); future['ordinary_yields'] = {'gold': 10}
        result = review(s, RULES, horizon=120, future=future)
        self.assertGreater(result['best']['review_utility'], 0)
        self.assertEqual(result['base_goal_status'], 'no_owned_base_path')
        self.assertEqual(result['preferred_action'], 'review_only_missing_base_path')

    def test_future_customer_cannot_cover_material(self):
        s = site(); future = branch(s); s['materials'] = [material(20)]
        with self.assertRaises(ValueError): evaluate(s, [2], RULES, future=future)

    def test_future_material_pays_cost_and_waits_for_completion(self):
        s = site(); s['materials'] = [material(working=False, worked=False)]
        result = evaluate(s, [2], RULES, future_materials=[dict(plot=11, ready_turn=15, cost=30,
                                                             legal=None, conflict=False)])
        entry = next(r for r in result['ledger']['culture'] if r['component'].startswith('workshop.material'))
        self.assertEqual(entry['start_turn'], 15)
        self.assertEqual(result['construction_cost'], 30)
        self.assertTrue(result['conditional_future'])

    def test_later_development_lowers_same_plan_value(self):
        s = site(); future = branch(s); first = evaluate(s, [2], RULES, future=future)
        future['ready_turn'] += 10; second = evaluate(s, [2], RULES, future=future)
        self.assertGreater(first['review_utility'], second['review_utility'])

    def test_unpriced_repairs_do_not_become_free_rebuilds(self):
        s = site(); s['pillaged_buildings'] = [2]
        self.assertIsNone(review(s, RULES)['best'])

    def test_missing_production_is_not_zero_turn_construction(self):
        s = site(); s['city']['production'] = None
        self.assertEqual(evaluate(s, [2, 3], RULES)['status'], 'production_estimate_needed')

    def test_duplicate_customer_and_material_records_fail(self):
        for key, row in (('materials', material()), ('customers', customer())):
            s = site(); s[key] = [row, copy.deepcopy(row)]
            with self.assertRaises(ValueError): evaluate(s, [2], RULES)

    def test_original_human_exclusion_is_not_specific_to_player_zero(self):
        s = site(); s['original_human'] = True
        with self.assertRaises(ValueError): evaluate(s, [2], RULES)

    def test_nonfinite_review_inputs_fail(self):
        with self.assertRaises(ValueError): evaluate(site(), [2], RULES, cost_scale=math.inf)


class CapturedCaseTests(unittest.TestCase):
    def test_kerma_upgrade_matches_independent_incremental_ledger(self):
        s = next(s for s in PACKET['sites'] if s['id'] == 'candidate150:p1:c393221:TAILORS:2165')
        result = review(s, RULES)['best']
        # Fashion ready at6, then74 turns: P2, G-1, C3 per turn, cost250.
        self.assertEqual(result['incremental_modelled_yields'], dict(production=148, gold=-74, culture=222))
        self.assertEqual(result['construction_cost'], 250)
        self.assertEqual(result['review_utility'], 148-74*0.5+222-250)
        self.assertEqual(review(s, RULES, horizon=40)['preferred_action'], 'retain_or_defer')

    def test_named_harbor_branch_pays_full_investment_before_any_recommendation(self):
        s = next(s for s in PACKET['sites'] if s['id'].startswith('shadow110:') and s['identity']['plot'] == 2189)
        future = customer('DISTRICT_HARBOR', 2188, 7, 131073)
        future.update(ready_turn=20, cost=120, maintenance=1, ordinary_yields={'gold': 3}, conflict=False)
        result = review(s, RULES, horizon=120, future=future)
        # P300 + G73*0.5 - (district45 + Workshop80 + customer120).
        self.assertEqual(result['best']['review_utility'], 91.5)
        self.assertEqual(result['preferred_action'], 'review_only_missing_base_path')

    def test_all_copied_cases_review_without_native_or_old_policy_imports(self):
        results = [review(s, RULES) for s in PACKET['sites']]
        self.assertEqual(len(results), 44)
        self.assertEqual(sum(r['best'] is not None for r in results), 41)
        self.assertTrue(all(not r['best']['deployable'] for r in results if r['best']))

    def test_six_new_sites_have_no_owned_mapped_supply(self):
        sites = [s for s in PACKET['sites'] if not s['quarter']['exists']]
        self.assertEqual(len(sites), 6)
        for s in sites:
            result = review(s, RULES)
            self.assertEqual(result['best']['materials']['base'], 0)
            self.assertEqual(result['best']['materials']['specialty'], 0)
            self.assertEqual(result['preferred_action'], 'retain_or_defer')

    def test_native_utility_and_old_policy_values_are_not_outputs(self):
        result = review(PACKET['sites'][0], RULES)
        self.assertNotIn('deltaQ8', result)
        self.assertNotIn('private_yield', result)
        self.assertIn('NOT native Q8', result['best']['utility_units'])


if __name__ == '__main__':
    unittest.main()
