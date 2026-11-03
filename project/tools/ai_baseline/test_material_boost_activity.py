import unittest
from material_boost_activity import routes,native_strategy_events,native_strategy_at

class Routes(unittest.TestCase):
 def fixture(self):
  row=dict(turn=43,player=4,system='Seek Tech Boost TECH_APPRENTICESHIP',tree='Build City Improvement',plot=1,improvement='IMPROVEMENT_MINE')
  boosts=[dict(TechnologyType='TECH_APPRENTICESHIP',CivicType=None,BoostClass='BOOST_TRIGGER_HAVE_X_IMPROVEMENTS')]
  care=dict(events=[dict(event='work_state',player=4,plot=1,turn=36,state='develop')],strategy=dict(transitions=[dict(player=4,turn=33,active=True)]))
  return row,boosts,care
 def test_repeated_route_records_not_independent_jobs(self):
  r,b,c=self.fixture();values=routes([r,dict(r,turn=44)],b,c);self.assertEqual(len(values),1);self.assertEqual(values[0]['reservation_log_records'],2);self.assertFalse(values[0]['persistent_job_identity_proven'])
 def test_first_observed_route_records_prior_care_and_strategy(self):
  r,b,c=self.fixture();v=routes([r],b,c)[0];self.assertTrue(v['gated_improvement_count_handler']);self.assertTrue(v['care_strategy_at_first_observation']['active']);self.assertEqual(v['last_care_record_at_or_before_first_reservation']['turn'],36)
 def test_future_care_not_backfilled(self):
  r,b,c=self.fixture();c['events'][0]['turn']=50;c['strategy']['transitions'][0]['turn']=50;v=routes([r],b,c)[0];self.assertIsNone(v['last_care_record_at_or_before_first_reservation']);self.assertIsNone(v['care_strategy_at_first_observation']['active'])
 def test_city_jobs_and_other_tree_not_labeled_boost_routes(self):
  r,b,c=self.fixture();self.assertEqual(routes([dict(r,system='City X'),dict(r,tree='Other')],b,c),[])
 def test_other_boost_handler_not_claimed_suppressed(self):
  r,b,c=self.fixture();b[0]['BoostClass']='OTHER';self.assertFalse(routes([r],b,c)[0]['gated_improvement_count_handler'])

class NativeStrategy(unittest.TestCase):
 def test_filters_other_strategy_and_observer(self):
  text='20,2,STRATEGY_CSC_AI_MATERIAL_BACKLOG,Following\n21,0,STRATEGY_CSC_AI_MATERIAL_BACKLOG,Following\n22,2,OTHER,Following'
  self.assertEqual(len(native_strategy_events(text,25)),1)
 def test_no_future_state_inferred(self):self.assertIsNone(native_strategy_at([dict(turn=50,player=2,status='Following')],2,45)['following'])
 def test_following_and_stopped_transitions_native(self):
  events=[dict(turn=20,player=2,status='Following'),dict(turn=30,player=2,status='Stopped')]
  self.assertTrue(native_strategy_at(events,2,25)['following']);self.assertFalse(native_strategy_at(events,2,35)['following']);self.assertFalse(native_strategy_at(events,2,20)['within_turn_ordering_proven'])
 def test_unrecognized_status_not_falsely_stopped(self):self.assertIsNone(native_strategy_at([dict(turn=20,player=2,status='Unknown')],2,25)['following'])

if __name__=='__main__':unittest.main()
