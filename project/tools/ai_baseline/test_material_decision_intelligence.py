import unittest
from material_decision_intelligence import reservations,preparation_operations,native_hash
class Decisions(unittest.TestCase):
 def test_only_successful_reservation_with_current_intent(self):
  text='\n'.join(['20, 1, City A, Build City Improvement, READY, Decode Trigger, Improve: IMPROVEMENT_FARM; Value: 123','20, 1, City A, Build City Improvement, FAILURE, Reserve Plot, Reserving plot 3 2','20, 1, City A, Build City Improvement, SUCCESS, Reserve Plot, Reserving plot -9999 -9999','20, 1, City A, Build City Improvement, SUCCESS, Reserve Plot, Reserving plot 3 2'])
  result=reservations(text,20,10);self.assertEqual(len(result),1);self.assertEqual((result[0]['plot'],result[0]['improvement'],result[0]['value']),(23,'IMPROVEMENT_FARM',123))
 def setup_case(self):
  case=dict(player=4,plot=23,turn=174,evidence=[dict(kind='native_operation_started',record=dict(unit=8))])
  event=dict(event='builder_operation_started',player=4,unit=8,turn=173,x=3,y=2,operation=native_hash('UNITOPERATION_REMOVE_IMPROVEMENT'))
  op=dict(player=4,unit=8,turn=173,operation='UNITOPERATION_REMOVE_IMPROVEMENT')
  return case,event,op
 def test_exact_same_unit_native_and_log_pair(self):
  c,e,o=self.setup_case();self.assertEqual(preparation_operations(c,[e],[o],[],10)[0]['name'],'UNITOPERATION_REMOVE_IMPROVEMENT')
 def test_queued_log_without_native_start_is_not_proof(self):
  c,e,o=self.setup_case();self.assertEqual(preparation_operations(c,[],[o],[],10),[])
 def test_native_start_without_operation_name_log_not_accepted(self):
  c,e,o=self.setup_case();self.assertEqual(preparation_operations(c,[e],[],[],10),[])
 def test_different_unit_or_plot_does_not_match(self):
  c,e,o=self.setup_case();e['unit']=9;self.assertEqual(preparation_operations(c,[e],[o],[],10),[])
  c,e,o=self.setup_case();e['x']=4;self.assertEqual(preparation_operations(c,[e],[o],[],10),[])
 def test_invalid_coordinate_requires_unique_tree_target(self):
  c,e,o=self.setup_case();e['x']=e['y']=-9999;target=dict(turn=173,player=4,unit=8,plot=23)
  self.assertEqual(len(preparation_operations(c,[e],[o],[target],10)),1)
  self.assertEqual(preparation_operations(c,[e],[o],[target,dict(target,plot=24)],10),[])
if __name__=='__main__':unittest.main()
