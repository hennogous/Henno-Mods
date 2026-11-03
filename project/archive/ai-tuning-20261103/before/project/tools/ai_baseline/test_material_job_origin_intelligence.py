import unittest
from material_job_origin_intelligence import origin,strategy_at,enrich

class Origins(unittest.TestCase):
 def setUp(self):self.boosts=[dict(TechnologyType='TECH_APPRENTICESHIP',CivicType=None,ImprovementType='IMPROVEMENT_MINE',NumItems=3),dict(TechnologyType=None,CivicType='CIVIC_FEUDALISM',ImprovementType='IMPROVEMENT_FARM',NumItems=6)]
 def test_native_technology_target_joins_exact_loaded_definition(self):
  v=origin('Seek Tech Boost TECH_APPRENTICESHIP',self.boosts);self.assertEqual(v['kind'],'boost');self.assertEqual(len(v['loaded_boost_rows']),1);self.assertEqual(v['loaded_boost_rows'][0]['NumItems'],3)
 def test_civic_target_is_separate(self):self.assertEqual(origin('Seek Civic Boost CIVIC_FEUDALISM',self.boosts)['loaded_boost_rows'][0]['NumItems'],6)
 def test_incidental_tech_word_in_city_not_boost_proof(self):self.assertEqual(origin('City LOC_CITY_TECH_APPRENTICESHIP',self.boosts)['kind'],'city')
 def test_unknown_target_keeps_missing_definition(self):self.assertEqual(origin('Seek Tech Boost TECH_UNKNOWN',self.boosts)['loaded_boost_rows'],[])
 def test_no_future_strategy_state_leaks_back(self):self.assertIsNone(strategy_at([dict(player=2,turn=50,active=True)],2,45)['active'])
 def test_other_player_and_later_transition_not_applied(self):
  rows=[dict(player=2,turn=20,active=True),dict(player=4,turn=21,active=False),dict(player=2,turn=50,active=False)]
  self.assertTrue(strategy_at(rows,2,45)['active'])
 def test_same_turn_transition_uses_export_order(self):self.assertFalse(strategy_at([dict(player=2,turn=20,active=True),dict(player=2,turn=20,active=False)],2,20)['active'])
 def test_missing_reservation_not_invented_as_city_job(self):self.assertIsNone(enrich(dict(player=2),self.boosts,[])['origin'])
 def test_improvement_must_match_boost_definition(self):
  case=dict(player=2,first_matching_reservation=dict(system='Seek Tech Boost TECH_APPRENTICESHIP',turn=45,improvement='IMPROVEMENT_FARM'))
  v=enrich(case,self.boosts,[dict(player=2,turn=20,active=True)])
  self.assertFalse(v['origin']['requested_improvement_matches_boost']);self.assertTrue(v['care_strategy_at_reservation']['active']);self.assertFalse(v['decision_utility_weights_observed'])

if __name__=='__main__':unittest.main()
