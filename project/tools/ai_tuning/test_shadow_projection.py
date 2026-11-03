import unittest
from copy import deepcopy
from shadow_projection import building_census, project, review_projection


def fixture():
    rule = dict(ID='river', ModifierOwner='BuildingModifiers', WhoIsTheOwner='MILL',
                CollectionType='COLLECTION_PLAYER_DISTRICTS', eligible=True,
                ProvideType='SelfBonus', YieldType='YIELD_PRODUCTION', computed_amount=1)
    raw = dict(turn=110, player=3, city=1, action_authorization=False,
               tiles=[dict(owner=3, purchase_city=c, district=36,
                           city_building_inventory=[dict(type='MILL', pillaged=c==1)]) for c in (1, 2, 3)],
               controls=[], candidates=[])
    core = dict(turn=110, cities=[dict(id=c, owner=3, buildings=[7]) for c in (1, 2, 3)])
    return raw, core, rule


class ProjectionTests(unittest.TestCase):
    def test_two_working_sources_stack_pillaged_source_does_not(self):
        raw, core, rule = fixture()
        cities, inventory = building_census(raw, core)
        result = project(dict(rules=[rule]), 1, cities, inventory)
        self.assertEqual(result['real']['YIELD_PRODUCTION'], 2)
        self.assertEqual(result['rules'][0]['active_source_instances'], 2)

    def test_local_collection_does_not_borrow_foreign_city(self):
        raw, core, rule = fixture()
        rule['CollectionType'] = 'COLLECTION_CITY_DISTRICTS'
        cities, inventory = building_census(raw, core)
        self.assertEqual(project(dict(rules=[rule]), 1, cities, inventory)['real']['YIELD_PRODUCTION'], 0)

    def test_missing_nonempty_census_is_unknown_not_zero(self):
        raw, core, rule = fixture(); raw['tiles'].pop()
        cities, inventory = building_census(raw, core)
        result = project(dict(rules=[rule]), 1, cities, inventory)
        self.assertIsNone(result['real']['YIELD_PRODUCTION'])
        self.assertTrue(result['gaps'])
        core['cities'][-1]['buildings'] = []
        cities, inventory = building_census(raw, core)
        self.assertEqual(project(dict(rules=[rule]), 1, cities, inventory)['real']['YIELD_PRODUCTION'], 1)

    def test_repeated_district_inventory_is_not_another_source(self):
        raw, core, rule = fixture(); raw['tiles'].append(deepcopy(raw['tiles'][1]))
        cities, inventory = building_census(raw, core)
        self.assertEqual(project(dict(rules=[rule]), 1, cities, inventory)['real']['YIELD_PRODUCTION'], 2)
        raw['tiles'][-1]['city_building_inventory'][0]['pillaged'] = True
        with self.assertRaises(ValueError): building_census(raw, core)

    def test_fraction_is_encoded_per_source_before_multiplication(self):
        raw, core, rule = fixture()
        # Three river edges at 0.5 encode as 1 per attachment, not floor(3*0.5*2)=3.
        rule['count'] = 3; rule['YieldChange'] = 0.5
        cities, inventory = building_census(raw, core)
        self.assertEqual(project(dict(rules=[rule]), 1, cities, inventory)['real']['YIELD_PRODUCTION'], 2)

    def test_other_player_cities_and_private_values_do_not_leak(self):
        raw, core, rule = fixture(); core['cities'].append(dict(id=1, owner=4, buildings=[7]))
        raw['tiles'].append(dict(owner=4, purchase_city=1, district=36,
                                city_building_inventory=[dict(type='MILL',pillaged=False)]))
        private = dict(rule, YieldType='YIELD_CSC_AI_PLACEMENT', computed_amount=999)
        cities, inventory = building_census(raw, core)
        self.assertEqual(project(dict(rules=[rule, private]), 1, cities, inventory)['real']['YIELD_PRODUCTION'], 2)

    def test_control_match_does_not_promote_native_preview_or_authority(self):
        raw, core, rule = fixture()
        raw['controls'] = [dict(city=1,plot=10,quarter='Q',preview=dict(rules=[rule],computed_real={}),
                                existing_adjacency=dict(YIELD_PRODUCTION=2,YIELD_GOLD=0))]
        before = deepcopy(raw)
        result = review_projection(raw,core,'synthetic')
        self.assertEqual(result['controls_matched'],1)
        self.assertFalse(result['native_plot_preview_validated'])
        self.assertFalse(result['candidate_total_adjacency_validated'])
        self.assertFalse(result['action_authorization'])
        self.assertEqual(raw,before)


if __name__ == '__main__': unittest.main()
