import copy,sqlite3,unittest
from material_resource_improvement_forecast import verify_loaded,verify_source,verify_final_snapshot,TYPES,PRIVATE,AMOUNT
from material_forecast_variants import variant,declared_database_delta

class ResourceForecast(unittest.TestCase):
 def fixture(self):
  values=[]
  for _ in range(2):
   db=sqlite3.connect(':memory:');self.addCleanup(db.close)
   db.executescript('CREATE TABLE Improvement_YieldChanges(ImprovementType,YieldType,YieldChange);CREATE TABLE Improvement_ValidResources(ImprovementType,ResourceType);CREATE TABLE Improvement_ValidTerrains(ImprovementType,TerrainType);CREATE TABLE Improvement_ValidFeatures(ImprovementType,FeatureType);')
   db.executemany('INSERT INTO Improvement_ValidResources VALUES(?,?)',[(t,'RESOURCE_'+str(i))for i,t in enumerate(TYPES)])
   db.execute("INSERT INTO Improvement_YieldChanges VALUES('IMPROVEMENT_FARM','YIELD_FOOD',1)")
   values.append(db)
  raw,current=values;current.executemany('INSERT INTO Improvement_YieldChanges VALUES(?,?,?)',[(t,PRIVATE,AMOUNT)for t in TYPES]);return raw,current
 def test_exact_three_loaded_rows_do_not_claim_native_response(self):
  raw,current=self.fixture();v=verify_loaded(current,raw);self.assertTrue(v['exact_three_direct_rows_added']);self.assertFalse(v['native_forecast_choice_response_proven']);self.assertIn('humans',v['scope'])
 def test_missing_wrong_amount_or_Farm_bonus_is_rejected(self):
  for sql in("DELETE FROM Improvement_YieldChanges WHERE ImprovementType='IMPROVEMENT_CAMP'","UPDATE Improvement_YieldChanges SET YieldChange=79 WHERE YieldType='YIELD_CSC_AI_PLACEMENT'","INSERT INTO Improvement_YieldChanges VALUES('IMPROVEMENT_FARM','YIELD_CSC_AI_PLACEMENT',80)"):
   raw,current=self.fixture();current.execute(sql)
   with self.subTest(sql=sql),self.assertRaises(AssertionError):verify_loaded(current,raw)
 def test_real_improvement_yield_drift_rejected(self):
  raw,current=self.fixture();current.execute("UPDATE Improvement_YieldChanges SET YieldChange=2 WHERE YieldType='YIELD_FOOD'")
  with self.assertRaises(AssertionError):verify_loaded(current,raw)
 def test_control_already_treated_rejected(self):
  raw,current=self.fixture();raw.execute('INSERT INTO Improvement_YieldChanges VALUES(?,?,?)',(TYPES[0],PRIVATE,AMOUNT))
  with self.assertRaises(AssertionError):verify_loaded(current,raw)
 def test_non_resource_only_improvement_scope_rejected(self):
  for table in('Improvement_ValidTerrains','Improvement_ValidFeatures'):
   raw,current=self.fixture();current.execute('INSERT INTO '+table+' VALUES(?,?)',(TYPES[0],'ANY'))
   with self.subTest(table=table),self.assertRaises(AssertionError):verify_loaded(current,raw)
 def test_existing_source_improvements_or_wrong_clock_rejected(self):
  source=dict(world=dict(turn=16,plots=[]));self.assertEqual(verify_source(source)['matching_improvements_observed'],0)
  for t in TYPES:
   source['world']['plots']=[dict(improvement=t)]
   with self.subTest(t=t),self.assertRaises(AssertionError):verify_source(source)
  with self.assertRaises(AssertionError):verify_source(dict(world=dict(turn=17,plots=[])))
 def test_native_endpoint_phase_and_complete_observation(self):
  primary=dict(turn=75,plots=[dict(index=1,owner=1,resource='HONEY',improvement='IMPROVEMENT_CAMP')]);snapshot=dict(turn=74,cities=[dict(plots=[dict(plot=1,owner=1,resource='HONEY',private=100,economic={})])]);boundary=dict(before=dict(turn=75,active=False,remaining=0),after=dict(turn=75,active=False,remaining=0))
  v=verify_final_snapshot(snapshot,primary,boundary);self.assertEqual(v['raw_UI_turn'],74);self.assertEqual(v['owned_treatment_improvements_observed'],1);self.assertFalse(v['forecast_private_effect_isolated'])
  for field in('missing','owner','duplicate','active'):
   s=copy.deepcopy(snapshot);b=copy.deepcopy(boundary)
   if field=='missing':s['cities']=[]
   if field=='owner':s['cities'][0]['plots'][0]['owner']=2
   if field=='duplicate':s['cities'][0]['plots']*=2
   if field=='active':b['after']['active']=True
   with self.subTest(field=field),self.assertRaises(AssertionError):verify_final_snapshot(s,primary,b)
 def test_explicit_variant_and_no_control_relaxation(self):
  v=variant('S','raw-resource','resource-improvement-forecast-v6');self.assertTrue(v['resource_improvement_forecast']);self.assertFalse(v['pasture_forecast']);self.assertEqual((v['files'],v['runtime_deltas']),(515,7));self.assertFalse(any(v[k]for k in('runtime_harvest_rule','measured_rule_legality','boost_gate','native_harvest_guard')))
  before={k:dict(rows=1,sha256='same')for k in('Resource_YieldChanges','Improvement_YieldChanges','Units')};raw={**before,'Resource_YieldChanges':dict(rows=2,sha256='raw')};after={**raw,'Improvement_YieldChanges':dict(rows=4,sha256='three')}
  self.assertEqual(set(declared_database_delta(before,after,treatment=True,resource_improvement_forecast=True,raw_control=raw)),{'Resource_YieldChanges','Improvement_YieldChanges'})
  with self.assertRaises(AssertionError):declared_database_delta(before,after,treatment=True,pasture_forecast=True,resource_improvement_forecast=True,raw_control=raw)
  with self.assertRaises(AssertionError):declared_database_delta(before,after,treatment=True,raw_control=raw)
  after['Units']=dict(rows=2,sha256='wrong')
  with self.assertRaises(AssertionError):declared_database_delta(before,after,treatment=True,resource_improvement_forecast=True,raw_control=raw)

if __name__=='__main__':unittest.main()
