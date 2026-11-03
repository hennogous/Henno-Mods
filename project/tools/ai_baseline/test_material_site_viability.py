import json,tempfile,unittest
from pathlib import Path
from material_site_viability import selected_materials,precommit

class MaterialSiteViability(unittest.TestCase):
 def fixture(self):
  c=dict(player=1,city=10,quarter='BAKERS',plot=42,observed_turn=69,plan_materials=[81,82])
  tiles=[dict(index=81,owner=1,resource=0,district=-1,revealed=True,material_visible=True,base_for=['BAKERS'],spec_for=[]),dict(index=82,owner=1,resource=25,district=0,revealed=True,material_visible=True,base_for=[],spec_for=['BAKERS'])]
  return c,dict(player=1,city=10,tiles=tiles)
 def test_numeric_resource_zero_valid_but_numeric_district_zero_blocked(self):
  c,city=self.fixture();r=selected_materials(c,city);self.assertEqual(r['district_free_owned_base'],1);self.assertEqual(r['district_free_owned_spec'],0);self.assertFalse(r['Both_structural_gate']);self.assertEqual(r['covered_materials'],[82])
 def test_missing_observation_is_unknown_not_a_true_Both_gate(self):
  c,city=self.fixture();city['tiles'].pop();r=selected_materials(c,city);self.assertIsNone(r['Both_structural_gate']);self.assertEqual(r['missing_observations'],[82])
 def test_latest_precommit_fact_selected_and_postcommit_ignored(self):
  c,city=self.fixture()
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);(root/'pending-commands').mkdir();(root/'commands').mkdir();(root/'pending-commands/12-zero-commit-69-1-10-BAKERS.lua').write_text('commit marker')
   def write(seq,kind):
    city['tiles'][1]['district']=kind
    (root/'commands'/f'{seq}-service-read-69.txt').write_text('CSC_SERVICE_NATIVE='+json.dumps(dict(turn=68,cities=[city]))+'\n')
   write(8,-1);write(10,0);write(13,-1);r=precommit(root,c);self.assertTrue(r['observed']);self.assertEqual(r['read_sequence'],10);self.assertFalse(r['Both_structural_gate']);self.assertEqual(r['raw_UI_turn'],68)

if __name__=='__main__':unittest.main()
