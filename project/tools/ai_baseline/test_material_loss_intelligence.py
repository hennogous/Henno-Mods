import unittest
from material_loss_intelligence import unit_operations,clear_targets,attribute,HARVEST
class LossTests(unittest.TestCase):
 def setUp(self):self.loss=dict(player=1,turn=21,plot=2533,resource=-1,previous_resource=1,owner=1,district=-1)
 def test_operation_log_player_is_third_column_and_request_not_completion(self):
  text="021, Adding, 1, UNIT_BUILDER (7), UNITOPERATION_HARVEST_RESOURCE (16)\n021, Can't Start, 1, UNIT_BUILDER (7), UNITOPERATION_HARVEST_RESOURCE (16)"
  ops=unit_operations(text,1,30,{1});self.assertEqual(len(ops),2);self.assertEqual(ops[0]['player'],1);self.assertEqual(attribute(self.loss,[],ops,[],74)['classification'],'unresolved')
 def test_last_charge_position_recovered_by_exact_unit_tree_target(self):
  text='21, 1, City A, Build City Improvement, SUCCESS, Reserve Plot, Reserving plot 17 34\n21, 1, City A, Build City Improvement, SUCCESS, Clear Plot, Clearing with 7'
  target=clear_targets(text,1,30,{1},74);event=dict(player=1,turn=21,unit=7,operation=HARVEST,x=-9999,y=-9999,charges=0)
  result=attribute(self.loss,[event],[],target,74);self.assertEqual(result['classification'],'native_harvest_confirmed');self.assertTrue(result['position_recovered_from_tree'])
 def test_other_unit_or_ambiguous_target_cannot_explain_loss(self):
  event=dict(player=1,turn=21,unit=7,operation=HARVEST,x=-9999,y=-9999)
  targets=[dict(player=1,turn=21,unit=7,plot=2533),dict(player=1,turn=21,unit=7,plot=2534)]
  self.assertEqual(attribute(self.loss,[event],[],targets,74)['classification'],'unresolved')
 def test_failed_reservation_does_not_reuse_stale_target(self):
  text='21, 1, City A, Build City Improvement, SUCCESS, Reserve Plot, Reserving plot 17 34\n21, 1, City A, Build City Improvement, FAILURE, Reserve Plot, Reserving plot -9999 -9999\n21, 1, City A, Build City Improvement, SUCCESS, Clear Plot, Clearing with 7'
  self.assertFalse(clear_targets(text,1,30,{1},74))
 def test_planned_farm_can_be_bound_to_exact_harvest_unit(self):
  text='21, 1, City A, Build City Improvement, READY, Decode Trigger, Improve: IMPROVEMENT_FARM; Value: 4661\n21, 1, City A, Build City Improvement, SUCCESS, Reserve Plot, Reserving plot 17 34\n21, 1, City A, Build City Improvement, SUCCESS, Clear Plot, Clearing with 7'
  target=clear_targets(text,1,30,{1},74);self.assertEqual(target[0]['planned_improvement'],'IMPROVEMENT_FARM');self.assertEqual(target[0]['job_value'],4661)
 def test_capture_is_not_resource_destruction(self):
  self.loss.update(resource=1,owner=2);self.assertEqual(attribute(self.loss,[],[],[],74)['classification'],'ownership_link_lost')
 def test_district_at_removal_does_not_invent_permanent_wonder(self):
  self.loss['district']=13;result=attribute(self.loss,[],[],[],74);self.assertEqual(result['classification'],'resource_removed_with_district_at_loss');self.assertIn('no permanent',result['limit'])
if __name__=='__main__':unittest.main()
