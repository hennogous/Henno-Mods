import copy,unittest
from material_forecast_contract import private_yield_parity,production_signature,database_delta,PRODUCTION_FIELDS
class Contracts(unittest.TestCase):
 def rows(self):return [dict(plot=1,resource='CATTLE',owner=2,private=160,economic={'food':2,'gold':0})]
 def test_reference_is_exact(self):self.assertTrue(private_yield_parity(self.rows(),self.rows(),{})['verified'])
 def test_treatment_is_additive_and_exact(self):
  actual=self.rows();actual[0]['private']=200
  self.assertTrue(private_yield_parity(self.rows(),actual,{'CATTLE':40})['economic_yields_equal'])
 def test_economic_owner_and_resource_changes_fail(self):
  for key,value in [('owner',3),('resource','WHEAT'),('economic',{'food':3,'gold':0}),('private',199)]:
   actual=self.rows();actual[0][key]=value
   with self.subTest(key=key),self.assertRaises(AssertionError):private_yield_parity(self.rows(),actual,{'CATTLE':40})
 def test_scope_or_duplicate_plots_fail(self):
  with self.assertRaises(AssertionError):private_yield_parity(self.rows(),[],{})
  with self.assertRaises(AssertionError):private_yield_parity(self.rows(),self.rows()*2,{})
 def test_production_parity_includes_queue_and_secondary_legality(self):
  row={k:0 for k in PRODUCTION_FIELDS};row.update(player=1,city=10,district_state={'can':True},queue_size=2)
  original={'cities':[row]};actual=copy.deepcopy(original);actual['cities'][0]['queue_size']=3
  self.assertNotEqual(production_signature(original),production_signature(actual))
  actual=copy.deepcopy(original);actual['cities'][0]['district_state']['can']=False
  self.assertNotEqual(production_signature(original),production_signature(actual))
 def test_reference_rejects_every_database_change(self):
  with self.assertRaises(AssertionError):database_delta({'A':1},{'A':2},treatment=False)
  self.assertEqual(database_delta({'A':1},{'A':1},treatment=False),[])
 def test_treatment_rejects_missing_or_extra_database_delta(self):
  for actual in ({'Resource_YieldChanges':1,'A':1},{'Resource_YieldChanges':2,'A':2}):
   with self.assertRaises(AssertionError):database_delta({'Resource_YieldChanges':1,'A':1},actual,treatment=True)
  self.assertEqual(database_delta({'Resource_YieldChanges':1,'A':1},{'Resource_YieldChanges':2,'A':1},treatment=True),['Resource_YieldChanges'])
if __name__=='__main__':unittest.main()
