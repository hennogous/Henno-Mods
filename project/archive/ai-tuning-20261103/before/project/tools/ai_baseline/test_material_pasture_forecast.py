import copy,sqlite3,unittest
from material_pasture_forecast import verify_loaded,verify_source,verify_final_snapshot,PASTURE,PRIVATE,AMOUNT
from material_forecast_variants import variant,declared_database_delta

class PastureForecast(unittest.TestCase):
 def boundary(self):return dict(before=dict(turn=75,active=False,remaining=0),after=dict(turn=75,active=False,remaining=0))
 def fixture(self):
  databases=[]
  for _ in range(2):
   db=sqlite3.connect(':memory:');self.addCleanup(db.close);db.execute('CREATE TABLE Improvement_YieldChanges(ImprovementType TEXT,YieldType TEXT,YieldChange INTEGER,PRIMARY KEY(ImprovementType,YieldType))');db.executemany('INSERT INTO Improvement_YieldChanges VALUES(?,?,?)',[(PASTURE,'YIELD_PRODUCTION',1),('IMPROVEMENT_FARM','YIELD_FOOD',1)]);databases.append(db)
  raw,current=databases;current.execute('INSERT INTO Improvement_YieldChanges VALUES(?,?,?)',(PASTURE,PRIVATE,AMOUNT));return raw,current
 def test_exact_native_row_is_loaded_scope_not_choice_response(self):
  raw,current=self.fixture();v=verify_loaded(current,raw);self.assertTrue(v['only_one_direct_row_added']);self.assertFalse(v['native_forecast_choice_response_proven']);self.assertIn('humans',v['scope'])
 def test_real_yield_drift_rejected(self):
  raw,current=self.fixture();current.execute("UPDATE Improvement_YieldChanges SET YieldChange=9 WHERE YieldType='YIELD_FOOD'")
  with self.assertRaises(AssertionError):verify_loaded(current,raw)
 def test_wrong_private_amount_or_extra_other_improvement_rejected(self):
  for mode in('amount','other'):
   raw,current=self.fixture()
   if mode=='amount':current.execute('UPDATE Improvement_YieldChanges SET YieldChange=81 WHERE YieldType=?',(PRIVATE,))
   else:current.execute('INSERT INTO Improvement_YieldChanges VALUES(?,?,?)',('IMPROVEMENT_MINE',PRIVATE,80))
   with self.subTest(mode=mode),self.assertRaises(AssertionError):verify_loaded(current,raw)
 def test_no_diagnostic_added_or_already_present_in_control_rejected(self):
  raw,current=self.fixture()
  with self.assertRaises(AssertionError):verify_loaded(raw,raw)
  raw.execute('INSERT INTO Improvement_YieldChanges VALUES(?,?,?)',(PASTURE,PRIVATE,AMOUNT))
  with self.assertRaises(AssertionError):verify_loaded(current,raw)
 def test_source_existing_observed_Pasture_requires_new_explicit_contract(self):
  initial=dict(world=dict(turn=16,plots=[dict(index=1,improvement='IMPROVEMENT_FARM')]));self.assertEqual(verify_source(initial)['existing_observed_Pastures'],0)
  initial['world']['plots'][0]['improvement']=PASTURE
  with self.assertRaises(AssertionError):verify_source(initial)
 def test_wrong_source_clock_rejected(self):
  with self.assertRaises(AssertionError):verify_source(dict(world=dict(turn=17,plots=[])))
 def test_forecast_arm_never_gets_a_harvest_rule_or_legality_exception(self):
  v=variant('S','raw-resource','pasture-forecast-v5');self.assertTrue(v['pasture_forecast']);self.assertFalse(v['runtime_harvest_rule']);self.assertFalse(v['native_harvest_guard']);self.assertFalse(v['measured_rule_legality']);self.assertIsNone(v['runtime_rule_token']);self.assertFalse(v['boost_gate']);self.assertEqual(v['files'],514);self.assertEqual(v['runtime_deltas'],6);self.assertTrue(v['needs_raw_control']);self.assertEqual(v['extra_SQL'],'CSC_AI_ImprovementForecast_Diagnostic.sql')
 def test_exact_declared_forecast_scope_and_no_other_native_table_change(self):
  before={k:dict(rows=1,sha256='same')for k in('Resource_YieldChanges','Improvement_YieldChanges','Units')};raw={**before,'Resource_YieldChanges':dict(rows=2,sha256='raw')};after={**raw,'Improvement_YieldChanges':dict(rows=3,sha256='pasture')}
  self.assertEqual(set(declared_database_delta(before,after,treatment=True,pasture_forecast=True,raw_control=raw)),{'Resource_YieldChanges','Improvement_YieldChanges'})
  after['Units']=dict(rows=2,sha256='wrong')
  with self.assertRaises(AssertionError):declared_database_delta(before,after,treatment=True,pasture_forecast=True,raw_control=raw)
 def test_final_native_snapshot_does_not_claim_isolated_effect(self):
  primary=dict(turn=75,plots=[dict(index=1,owner=2,resource='RESOURCE_CATTLE',improvement=PASTURE,pillaged=False)])
  snapshot=dict(turn=75,cities=[dict(plots=[dict(plot=1,owner=2,resource='RESOURCE_CATTLE',private=120,economic=dict(YIELD_FOOD=3))])]);v=verify_final_snapshot(snapshot,primary,self.boundary());self.assertEqual(v['owned_Pastures_observed'],1);self.assertFalse(v['forecast_private_effect_isolated'])
  snapshot['cities'][0]['plots'][0]['owner']=3
  with self.assertRaises(AssertionError):verify_final_snapshot(snapshot,primary,self.boundary())
 def test_raw_ui_previous_turn_is_preserved_only_inside_exact_inactive_native_boundary(self):
  snapshot=dict(turn=74,cities=[]);primary=dict(turn=75,plots=[]);self.assertEqual(verify_final_snapshot(snapshot,primary,self.boundary())['raw_UI_turn'],74)
  snapshot['turn']=73
  with self.assertRaises(AssertionError):verify_final_snapshot(snapshot,primary,self.boundary())
  snapshot['turn']=75;boundary=self.boundary();boundary['after']['active']=True
  with self.assertRaises(AssertionError):verify_final_snapshot(snapshot,primary,boundary)
 def test_missing_or_duplicate_native_endpoint_plot_is_not_silently_zero(self):
  primary=dict(turn=75,plots=[dict(index=1,owner=2,improvement=PASTURE)]);snapshot=dict(turn=75,cities=[])
  with self.assertRaises(AssertionError):verify_final_snapshot(snapshot,primary,self.boundary())
  plot=dict(plot=1,owner=2,private=80,economic={});snapshot['cities']=[dict(plots=[plot,plot])]
  with self.assertRaises(AssertionError):verify_final_snapshot(snapshot,primary,self.boundary())
 def test_no_implicit_default_scope_relaxation_or_conflation(self):
  before={'Resource_YieldChanges':dict(rows=1,sha256='same'),'Improvement_YieldChanges':dict(rows=1,sha256='same')};raw={**before,'Resource_YieldChanges':dict(rows=2,sha256='raw')};after={**raw,'Improvement_YieldChanges':dict(rows=2,sha256='pasture')}
  for other in('default','boost','harvest'):
   kwargs={}if other=='default'else dict(pasture_forecast=True,**({'boost_gate':True}if other=='boost'else{'native_harvest_guard':True}))
   with self.subTest(other=other),self.assertRaises(AssertionError):declared_database_delta(before,after,treatment=True,raw_control=raw,**kwargs)

if __name__=='__main__':unittest.main()
