import copy,unittest
from material_forecast_comparison import case_state,harvest_case_union
class Supply(unittest.TestCase):
 def fixture(self):
  plot=dict(index=1,resource='CATTLE',owner=2,improvement='PASTURE',pillaged=False)
  site=dict(plot=2,quarter='BAKERS',player=2,complete=True,pillaged=False,producer_built=True,materials=[dict(plot=1,category='base',resource='CATTLE',owner=2,improvement=True,pillaged=False)])
  return plot,site,[dict(plot=2,quarter='BAKERS',player=2)]
 def test_retained_resource_without_quarter_is_not_working_supply(self):
  p,s,q=self.fixture();v=case_state(p,'CATTLE',[],q);self.assertTrue(v['resource_present_at_endpoint']);self.assertFalse(v['working_material_for_reference_Quarter']);self.assertFalse(v['functioning_reference_producer'])
 def test_unimproved_or_foreign_is_not_working_supply(self):
  for field,value in [('improvement',False),('owner',3),('pillaged',True)]:
   p,s,q=self.fixture();s['materials'][0][field]=value
   with self.subTest(field=field):self.assertFalse(case_state(p,'CATTLE',[s],q)['working_material_for_reference_Quarter'])
 def test_working_source_does_not_imply_a_producer(self):
  for field,value in [('producer_built',False),('complete',False),('pillaged',True)]:
   p,s,q=self.fixture();s[field]=value;v=case_state(p,'CATTLE',[s],q)
   with self.subTest(field=field):self.assertTrue(v['working_material_for_reference_Quarter']);self.assertFalse(v['functioning_reference_producer'])
 def test_full_endpoint_chain_is_separate_from_uninterrupted_proof(self):
  p,s,q=self.fixture();v=case_state(p,'CATTLE',[s],q);self.assertTrue(v['functioning_reference_producer']);self.assertFalse(v['uninterrupted_material_availability_proven'])
 def test_resource_replaced_even_with_improvement_is_not_supply(self):
  p,s,q=self.fixture();p['resource']=None;p['improvement']='FARM';v=case_state(p,'CATTLE',[s],q);self.assertFalse(v['resource_present_at_endpoint']);self.assertFalse(v['functioning_reference_producer'])
 def test_different_quarter_on_same_tile_does_not_count(self):
  p,s,q=self.fixture();s['quarter']='TAILORS';self.assertFalse(case_state(p,'CATTLE',[s],q)['functioning_reference_producer'])
 def test_valid_alternative_quarter_can_succeed_without_reference_plot(self):
  p,s,q=self.fixture();s['plot']=3;v=case_state(p,'CATTLE',[s],q,[dict(plot=3,quarter='BAKERS',player=2)])
  self.assertFalse(v['functioning_reference_producer']);self.assertTrue(v['any_functioning_matching_producer']);self.assertTrue(v['working_material_for_any_matching_Quarter'])
class CaseUnion(unittest.TestCase):
 def test_treatment_only_loss_is_included(self):
  decisions=[dict(cases=[dict(plot=1,resource='CATTLE',harvest_turn=21)]),dict(cases=[dict(plot=2,resource='SHEEP',harvest_turn=45)])]
  values=harvest_case_union(decisions)
  self.assertEqual([x['plot']for x in values],[1,2]);self.assertEqual(set(values[1]['cases']),{'raw-resource'})
 def test_shared_loss_is_one_focus_with_both_raw_records(self):
  a=dict(plot=1,resource='CATTLE',harvest_turn=21)
  values=harvest_case_union([dict(cases=[a]),dict(cases=[dict(a)])])
  self.assertEqual(len(values),1);self.assertEqual(set(values[0]['cases']),{'reference','raw-resource'})
 def test_repeated_harvest_and_resource_identity_not_dropped(self):
  values=harvest_case_union([dict(cases=[]),dict(cases=[dict(plot=1,resource='SHEEP',harvest_turn=45),dict(plot=1,resource='SHEEP',harvest_turn=49),dict(plot=1,resource='CATTLE',harvest_turn=50)])])
  self.assertEqual(len(values),2);self.assertEqual(len(next(v for v in values if v['resource']=='SHEEP')['cases']['raw-resource']),2)

if __name__=='__main__':unittest.main()
