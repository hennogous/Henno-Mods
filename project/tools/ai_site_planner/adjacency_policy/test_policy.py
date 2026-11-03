import copy,unittest
from policy import shortlist

def fixture():
 return dict(turn=20,originalAI=[1,2],currentHumans=[0],candidates=[dict(player=1,city=7,district=8,plot=30,quarter='BAKERS',production=2,gold=2,total=4,materialOnSite=False,legal=True)])
class PolicyTests(unittest.TestCase):
 def test_threshold_inclusive(self):self.assertEqual(len(shortlist(fixture())['entries']),1)
 def test_below_threshold(self):
  s=fixture();s['candidates'][0].update(production=1,total=3);self.assertEqual(shortlist(s)['entries'],[])
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
if __name__=='__main__':unittest.main()
