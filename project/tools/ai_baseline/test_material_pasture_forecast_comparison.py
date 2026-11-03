import copy,json,tempfile,unittest
from pathlib import Path
import material_pasture_forecast_comparison as m

class FirstPlans(unittest.TestCase):
 def row(self,turn,imp='IMPROVEMENT_FARM',player=1):return dict(turn=turn,improvement=imp,player=player,tree='Build City Improvement',plot=2533)
 def test_missing_plans_are_unknown(self):
  x=m.first_logged_plans([]);self.assertFalse(x['observed']);self.assertIsNone(x['turn']);self.assertEqual(m.plan_change(x,x)['comparison'],'UNOBSERVED')
 def test_duplicate_rows_are_not_multiple_choices(self):
  row=self.row(20);v=m.first_logged_plans([row,row]);self.assertEqual(v['improvements'],['IMPROVEMENT_FARM']);self.assertFalse(v['ambiguous'])
 def test_first_turn_competing_choices_never_count_as_clean_response(self):
  old=m.first_logged_plans([self.row(20)]);new=m.first_logged_plans([self.row(19,'IMPROVEMENT_PASTURE'),self.row(19)]);self.assertTrue(new['ambiguous']);self.assertFalse(m.plan_change(old,new)['first_Farm_to_Pasture_observed'])
 def test_later_pasture_does_not_rewrite_initial_Farm(self):
  x=m.first_logged_plans([self.row(27,'IMPROVEMENT_PASTURE'),self.row(20)]);self.assertEqual(x['turn'],20);self.assertEqual(x['improvements'],['IMPROVEMENT_FARM'])
 def test_same_owner_single_logged_change_is_observed_not_hidden_utility_proof(self):
  v=m.plan_change(m.first_logged_plans([self.row(20)]),m.first_logged_plans([self.row(18,'IMPROVEMENT_PASTURE')]));self.assertTrue(v['first_Farm_to_Pasture_observed']);self.assertFalse(v['hidden_commitment_or_internal_utility_proven'])
 def test_changed_owner_or_multiple_first_players_is_not_same_actor_response(self):
  a=m.first_logged_plans([self.row(20)]);b=m.first_logged_plans([self.row(19,'IMPROVEMENT_PASTURE',2)]);self.assertFalse(m.plan_change(a,b)['first_Farm_to_Pasture_observed'])
 def test_union_preserves_new_treatment_harms_and_unknown_resource(self):
  a=dict(loss_attribution=dict(cases=[dict(plot=1,prior_resource='RESOURCE_CATTLE')]))
  b=dict(loss_attribution=dict(cases=[dict(plot=2,prior_resource='RESOURCE_SHEEP'),dict(plot=3)]));rows=m.loss_union([a,b]);self.assertEqual([r['plot']for r in rows],[1,2,3]);self.assertIn('pasture_forecast',rows[1]['losses']);self.assertIsNone(rows[2]['resource'])
 def test_supplemental_helper_and_no_activation_checks(self):
  with tempfile.TemporaryDirectory()as temp:
   r=Path(temp);(r/'pending-commands').mkdir();helper=r/'helper.py';helper.write_text('def activate(): pass\n');saved=r/'snapshot.py';saved.write_bytes(helper.read_bytes());value=dict(verified=True,worker_pins_file_not_edited=True,helper_import_only=True,activation_guard_OFF=True,imported_helper=str(helper),source_snapshot=str(saved),identical_to_prelaunch_ended418_snapshot=dict(archive=str(saved)),sha256=m.sha(helper));(r/'supplemental-import-provenance.json').write_text(json.dumps(value));self.assertTrue(m.supplemental_provenance(r)['verified']);(r/'pending-commands/1.lua').write_text('CSC_NATIVE_HARVEST_RULE.Begin({});')
   with self.assertRaises(AssertionError):m.supplemental_provenance(r)


if __name__=='__main__':unittest.main()
