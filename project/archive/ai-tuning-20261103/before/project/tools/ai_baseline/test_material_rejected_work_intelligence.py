import copy,unittest
import material_rejected_work_intelligence as m
class RejectionTests(unittest.TestCase):
 def fixture(self):
  op=dict(turn=21,player=1,unit=327683,unit_type='UNIT_BUILDER',mode="Can't Start",operation='UNITOPERATION_HARVEST_RESOURCE')
  link=dict(turn=21,player=1,unit=327683,target=dict(plot=2533),intent=dict(improvement='IMPROVEMENT_FARM'),clear_node_result='SUCCESS')
  return op,link
 def test_tree_success_cannot_turn_native_rejection_into_success(self):
  op,link=self.fixture();v=m.rejected_routes([op],[link],[])[0];self.assertEqual(v['plot'],2533);self.assertTrue(v['no_matching_native_start_observed']);self.assertFalse(v['exact_build_improvement_parameter_proven'])
 def test_conflicting_same_unit_targets_stay_unknown(self):
  op,link=self.fixture();second=copy.deepcopy(link);second['target']['plot']=2534;v=m.rejected_routes([op],[link,second],[])[0];self.assertIsNone(v['plot']);self.assertEqual(v['ambiguous_target_observations'][0]['candidate_plots'],[2533,2534])
 def test_same_numeric_unit_other_player_does_not_match(self):
  op,link=self.fixture();link['player']=2;self.assertIsNone(m.rejected_routes([op],[link],[])[0]['plot'])
 def test_adding_is_not_a_rejection(self):
  op,link=self.fixture();op['mode']='Adding';self.assertEqual(m.rejected_routes([op],[link],[]),[])
 def test_duplicate_log_rows_are_not_claimed_as_independent_requests(self):
  op,link=self.fixture();v=m.rejected_routes([op,op],[link],[])[0];self.assertEqual(v['rejection_log_records'],2);self.assertEqual(v['unique_rejection_turns'],1)
 def test_later_matching_start_is_preserved_with_rejection(self):
  op,link=self.fixture();event=dict(turn=21,player=1,unit=327683,operation=m.native_hash(op['operation']));v=m.rejected_routes([op],[link],[event])[0];self.assertFalse(v['no_matching_native_start_observed']);self.assertEqual(v['native_start_events'],[event])
 def test_clear_zero_is_not_a_unit_target_binding(self):
  text='21, 1, City Meroe, Build City Improvement, SUCCESS, Reserve Plot, Reserving plot 17 34\n21, 1, City Meroe, Build City Improvement, READY, Clear Plot, Clearing with 0\n';self.assertEqual(m.tree_work_links(text,16,25,74),[])

class DevelopmentTests(unittest.TestCase):
 def fixture(self):return dict(event='work_state',state='working',previous='develop',turn=28,player=1,plot=2533,resource=1)
 def test_exact_player_turn_plot_build_event_is_required_for_unit_attribution(self):
  e=self.fixture();native=dict(player=1,turn=28,unit=589829,x=17,y=34,operation=m.native_hash('UNITOPERATION_BUILD_IMPROVEMENT'));v=m.development_episodes([e],[native],[],74)[0];self.assertTrue(v['unit_attribution_proven']);self.assertIsNone(v['endpoint_plot_observation'])
 def test_last_charge_invalid_coordinates_and_other_plot_remain_unattributed(self):
  e=self.fixture();native=[dict(player=1,turn=28,unit=1,x=-9999,y=-9999,operation=m.native_hash('UNITOPERATION_BUILD_IMPROVEMENT')),dict(player=1,turn=28,unit=2,x=18,y=34,operation=m.native_hash('UNITOPERATION_BUILD_IMPROVEMENT'))];v=m.development_episodes([e],native,[],74)[0];self.assertFalse(v['unit_attribution_proven']);self.assertEqual(len(v['same_player_turn_native_build_candidates']),2)
 def test_initial_working_and_repairs_not_counted_as_development(self):
  e=self.fixture()
  for previous in('new','repair'):
   e['previous']=previous;self.assertEqual(m.development_episodes([e],[],[],74),[])


if __name__=='__main__':unittest.main()
