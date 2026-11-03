import copy,unittest
from policy import shortlist,penalty,PROFILE
from daemon import validate_entries,validate_snapshot

def fixture():
 return dict(turn=20,originalAI=[1,2],currentHumans=[0],candidates=[dict(player=1,city=7,district=8,plot=30,quarter='BAKERS',production=2,gold=2,total=4,materialOnSite=False,legal=True)])
class PolicyTests(unittest.TestCase):
 def test_threshold_inclusive(self):self.assertEqual(len(shortlist(fixture())['entries']),1)
 def test_below_threshold(self):
  s=fixture();s['candidates'][0].update(production=1,total=3);self.assertEqual(shortlist(s)['entries'][0]['delta'],-65536)
 def test_highest_total_per_city(self):
  s=fixture();r=copy.deepcopy(s['candidates'][0]);r.update(plot=31,production=3,total=5);s['candidates'].append(r);self.assertEqual(shortlist(s)['entries'][0]['plot'],31)
 def test_quarters_compete_in_one_city(self):
  s=fixture();r=copy.deepcopy(s['candidates'][0]);r.update(quarter='TAILORS',district=9,total=6,production=4);s['candidates'].append(r);self.assertEqual(shortlist(s)['entries'][0]['district'],9)
 def test_two_cities(self):
  s=fixture();r=copy.deepcopy(s['candidates'][0]);r.update(city=8,plot=31);s['candidates'].append(r);self.assertEqual(len(shortlist(s)['entries']),2)
 def test_material_preservation(self):
  s=fixture();s['candidates'][0]['materialOnSite']=True;self.assertEqual(shortlist(s)['entries'],[])
 def test_human_rejected(self):
  s=fixture();s['currentHumans']=[1];self.assertRaises(ValueError,shortlist,s)
 def test_other_player_rejected(self):
  s=fixture();s['candidates'][0]['player']=3;self.assertRaises(ValueError,shortlist,s)
 def test_duplicate_rejected(self):
  s=fixture();s['candidates']*=2;self.assertRaises(ValueError,shortlist,s)
 def test_nonfinite_rejected(self):
  s=fixture();s['candidates'][0]['total']=float('nan');self.assertRaises(ValueError,shortlist,s)
 def test_stale_flags_removed(self):
  self.assertTrue(shortlist(fixture())['entries']);s=fixture();s['candidates']=[];self.assertEqual(shortlist(s)['entries'],[])
 def test_endpoint(self):
  s=fixture();s['turn']=101;self.assertRaises(ValueError,shortlist,s)
 def test_penalty_gradient_and_cap(self):
  self.assertEqual([penalty(x)for x in (5,4,3.5,3,2,1,0,-1)],[0,0,-32768,-65536,-131072,-196608,-262144,-262144])
 def test_good_and_many_weak_in_same_city(self):
  s=fixture()
  for plot in (31,32):
   r=copy.deepcopy(s['candidates'][0]);r.update(plot=plot,production=0,total=2);s['candidates'].append(r)
  p=shortlist(s);self.assertEqual(len(p['entries']),3);self.assertEqual(len(p['penalized']),2)
  validate_entries(p['entries'],dict(originalAI=[1,2],districtIndices=[8,9],width=74,height=46))
 def test_unselected_good_is_neutral(self):
  s=fixture();r=copy.deepcopy(s['candidates'][0]);r['plot']=31;s['candidates'].append(r)
  self.assertEqual([e['plot']for e in shortlist(s)['entries']],[30])
 def test_old_weak_disappears_on_refresh(self):
  s=fixture();s['candidates'][0].update(production=1,total=3);self.assertLess(shortlist(s)['entries'][0]['delta'],0)
  s['candidates'][0].update(production=2,total=4);self.assertGreater(shortlist(s)['entries'][0]['delta'],0)
 def test_native_pair_keys_and_bounds(self):
  config=dict(originalAI=[1],districtIndices=[8,9],width=74,height=46)
  e=dict(player=1,city=7,district=8,plot=30,delta=-65536)
  validate_entries([e,dict(e,district=9),dict(e,plot=31)],config)
  for rows in ([e,e],[dict(e,delta=0)],[dict(e,delta=-262145)],[dict(e,delta=1)]):
   self.assertRaises(ValueError,validate_entries,rows,config)
 def test_native_snapshot_exact_pair_and_signed_arithmetic(self):
  config=dict(originalAI=[1],districtIndices=[8,9],width=74,height=46)
  entries=[dict(player=1,city=7,district=8,plot=30,delta=-65536),dict(player=1,city=7,district=9,plot=31,delta=1048576)]
  records=[dict(player=1,city=7,district=8,plot=30,k='net',base=5000,result=-60536,reason=0),dict(player=1,city=7,district=9,plot=31,k='net',base=100,result=1048676,reason=0),dict(player=1,city=7,district=2,plot=40,k='best',base=400,result=400,reason=0)]
  value=dict(profile=PROFILE,read_only=False,entries=entries,records=records,stats=dict(records=3,entryCount=2,mode=2,active=0,changed=2,errors=0,fatal=0))
  self.assertFalse(validate_snapshot(value,config))
  value['records'][0]['plot']=31;self.assertRaises(ValueError,validate_snapshot,value,config)
 def test_soft_floor_does_not_cross_native_no_result(self):
  config=dict(originalAI=[1],districtIndices=[8],width=74,height=46)
  value=dict(profile=PROFILE,read_only=False,entries=[dict(player=1,city=7,district=8,plot=30,delta=-262144)],records=[dict(player=1,city=7,district=8,plot=30,k='net',base=-1000000,result=-1048576,reason=0)],stats=dict(records=1,entryCount=1,mode=2,active=0,changed=1,errors=0,fatal=0))
  self.assertFalse(validate_snapshot(value,config));self.assertGreater(-1048576*1.5,-2559744)
if __name__=='__main__':unittest.main()
