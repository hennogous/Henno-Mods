"""Focused integration checks against pinned real archive, not native outcome tests."""
import unittest
from archived_site_cases import archived_cases


class ArchivedSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = archived_cases()

    def test_real_partial_cases_never_become_complete_or_ranked(self):
        self.assertEqual(self.report['counts'], {'partial_evaluated': 3, 'ai_existing_chains': 2,
                                                'original_human_excluded': 1, 'complete_sites': 0, 'ranked_sites': 0})
        for case in self.report['partial_cases']:
            result = case['result']
            self.assertEqual(result['recommendation'], 'insufficient_evidence')
            self.assertEqual(result['current']['band'], 'unknown')
            self.assertIsNone(result['current']['YIELD_PRODUCTION'])
            self.assertIsNone(result['current']['YIELD_GOLD'])
            self.assertTrue(all(value is None for value in result['costs'].values()))
            self.assertEqual(result['current_supply'], [])

    def test_existing_totals_and_supply_are_kept_distinct(self):
        tailors, bakers = self.report['partial_cases'][:2]
        self.assertEqual(tailors['site']['source_kind'], 'observed_existing')
        self.assertEqual(tailors['site']['observed_district_yields']['value']['YIELD_PRODUCTION'], 4)
        self.assertEqual(tailors['site']['observed_district_yields']['value']['YIELD_GOLD'], 2)
        self.assertEqual([m['state'] for m in tailors['result']['materials']],
                         ['unknown_supply_eligibility', 'unknown_supply_eligibility'])
        self.assertEqual([m['state'] for m in bakers['result']['materials']],
                         ['needs_development', 'needs_development', 'needs_development'])
        self.assertNotIn('legal', tailors['site'])
        self.assertFalse(tailors['result']['both_service_potential']['current_mapped_supply'])

    def test_original_human_occupied_material_control_is_withheld(self):
        control = self.report['partial_cases'][2]
        self.assertFalse(control['ai_recommendation_eligible'])
        future = control['result']['future'][0]
        self.assertEqual(future['status'], 'withheld')
        self.assertIn('rejected legal', future['issues'])
        self.assertIsNone(future['incremental_real'])
        self.assertIsNone(control['result']['future_total_increment'])


if __name__ == '__main__':
    unittest.main()
