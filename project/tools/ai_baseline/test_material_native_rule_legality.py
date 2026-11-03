import copy,unittest
from material_native_rule_legality import extract_changes,verify_measured_change,ACCEPTED,REJECTED,NO_LOCATION,LOCATION_MESSAGE

class Legality(unittest.TestCase):
 def fixture(self,all_removed=False):
  tile=lambda i,res:dict(index=i,resource=res,owner=1,price=0,feature=-1,potential_legal=dict(BAKERS=True),current_legal=dict(BAKERS=True),native_projection_verified=True)
  tiles=[tile(1,1)]if all_removed else[tile(1,1),tile(2,-1)]
  state=dict(can_produce=True,placed=False,exists=False,secondary_result={ACCEPTED:[x['index']for x in tiles],REJECTED:[]})
  city=dict(player=1,city=7,production=10,queue_size=1,current_production_hash=5,population=2,tiles=tiles,district_state=dict(BAKERS=state))
  before=dict(turn=16,cities=[city]);after=copy.deepcopy(before);c=after['cities'][0];t=c['tiles'][0];t['potential_legal']['BAKERS']=False;t['current_legal']['BAKERS']=False;t['native_projection_verified']=False
  q=c['district_state']['BAKERS'];q['secondary_result']={REJECTED:[1]}
  if all_removed:q['can_produce']=False;q['secondary_result'][NO_LOCATION]=LOCATION_MESSAGE
  else:q['secondary_result'][ACCEPTED]=[2]
  runtime=dict(turn=16,ui_turn=16,active=False,definition='TRAIT_MAORI_PREVENT_HARVEST',instances=[dict(player=i,runtime_id=str(i),active=True)for i in range(1,6)],ledger=dict(status='confirmed',attempted=[1,2,3,4,5],returned=[1,2,3,4,5]))
  proof=dict(verified_zero_turn_rule_change=True,native_rule_definition='TRAIT_MAORI_PREVENT_HARVEST',turn=16,measured_legality_changes=extract_changes(before,after))
  return before,after,proof,runtime
 def test_resource_restriction_records_change_without_mutating_native_facts(self):
  b,a,p,r=self.fixture();saved=copy.deepcopy(a);v=verify_measured_change(b,a,p,r);self.assertEqual(a,saved);self.assertEqual(v['district_changes'][0]['removed_plots'],[1]);self.assertFalse(a['cities'][0]['tiles'][0]['current_legal']['BAKERS'])
 def test_all_owned_locations_lost_can_close_but_never_unlock_quarter(self):
  b,a,p,r=self.fixture(True);self.assertFalse(verify_measured_change(b,a,p,r)['district_changes'][0]['can_produce_after'])
 def test_empty_plot_cannot_be_masked_as_resource_rule(self):
  b,a,p,r=self.fixture();b['cities'][0]['tiles'][0]['resource']=a['cities'][0]['tiles'][0]['resource']=-1
  with self.assertRaises(AssertionError):verify_measured_change(b,a,p,r)
 def test_city_production_queue_population_or_current_item_drift_rejected(self):
  for key in('production','queue_size','population','current_production_hash'):
   b,a,p,r=self.fixture();a['cities'][0][key]+=1
   with self.subTest(key=key),self.assertRaises(AssertionError):verify_measured_change(b,a,p,r)
 def test_resource_owner_or_price_drift_rejected(self):
  for key in('resource','owner','price'):
   b,a,p,r=self.fixture();a['cities'][0]['tiles'][0][key]+=1
   with self.subTest(key=key),self.assertRaises(AssertionError):verify_measured_change(b,a,p,r)
 def test_legal_gains_rejected(self):
  b,a,p,r=self.fixture();a['cities'][0]['tiles'][0]['current_legal']['BAKERS']=True;a['cities'][0]['tiles'][1]['current_legal']['BAKERS']=False;b['cities'][0]['tiles'][0]['current_legal']['BAKERS']=False
  with self.assertRaises(AssertionError):verify_measured_change(b,a,p,r)
 def test_other_failure_reason_cannot_be_hidden(self):
  b,a,p,r=self.fixture();a['cities'][0]['district_state']['BAKERS']['secondary_result']['OTHER']=['Missing research']
  with self.assertRaises(AssertionError):verify_measured_change(b,a,p,r)
 def test_false_can_produce_requires_no_remaining_location_and_exact_reason(self):
  b,a,p,r=self.fixture();a['cities'][0]['district_state']['BAKERS']['can_produce']=False
  with self.assertRaises(AssertionError):verify_measured_change(b,a,p,r)
 def test_runtime_scope_or_active_proof_required(self):
  for mode in('missing','observer','inactive'):
   b,a,p,r=self.fixture()
   if mode=='missing':p=None
   elif mode=='observer':r['instances'][0]['player']=0
   else:r['instances'][0]['active']=False
   with self.subTest(mode=mode),self.assertRaises((AssertionError,TypeError)):verify_measured_change(b,a,p,r)
 def test_lua_quarter_map_order_and_archived_proof_order_are_not_semantics(self):
  b,a,p,r=self.fixture()
  for packet in(b,a):
   city=packet['cities'][0]
   city['district_state']['TAILORS']=copy.deepcopy(city['district_state']['BAKERS'])
   for tile in city['tiles']:
    for field in('potential_legal','current_legal'):tile[field]['TAILORS']=tile[field]['BAKERS']
  p['measured_legality_changes']=extract_changes(b,a)
  p['measured_legality_changes']['district_changes'].reverse()
  a['cities'][0]['district_state']=dict(reversed(list(a['cities'][0]['district_state'].items())))
  self.assertEqual(len(verify_measured_change(b,a,p,r)['district_changes']),2)
 def test_duplicate_proof_transition_is_rejected(self):
  b,a,p,r=self.fixture();p['measured_legality_changes']['district_changes']*=2
  with self.assertRaises(AssertionError):verify_measured_change(b,a,p,r)
 def test_measured_case_must_match_exactly(self):
  b,a,p,r=self.fixture();p['measured_legality_changes']['tile_changes'][0]['plot']=99
  with self.assertRaises(AssertionError):verify_measured_change(b,a,p,r)
 def test_duplicate_or_unexplained_rejected_plot_rejected(self):
  for rejected in([1,1],[1,2]):
   b,a,p,r=self.fixture();a['cities'][0]['district_state']['BAKERS']['secondary_result'][REJECTED]=rejected
   with self.subTest(rejected=rejected),self.assertRaises(AssertionError):verify_measured_change(b,a,p,r)
 def test_only_observation_cache_metadata_is_ignored(self):
  b,a,p,r=self.fixture();a['delta_checks']=dict(calls=2);a['cities'][0]['geography_cache_hit']=True;a['cities'][0]['delta_full_read_turn']=16;verify_measured_change(b,a,p,r)

if __name__=='__main__':unittest.main()
