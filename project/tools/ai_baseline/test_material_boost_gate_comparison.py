import unittest
from material_boost_log import boost_records,events_for_job
from material_boost_gate_comparison import loss_union,observed_state

class BoostEvidence(unittest.TestCase):
 def test_filters_turns_players_and_preserves_unknown_label(self):
  text='Game Turn, Player, Boosted System, Progress\n15,2,TECH_X,Old\n16,2,TECH_X,Unstarted\n17,0,TECH_X,Observer\n18,2,TECH_X,Custom\n76,2,TECH_X,Late'
  rows=boost_records(text,75);self.assertEqual([r['turn']for r in rows],[16,18]);self.assertEqual(rows[1]['native_progress_label'],'Custom')
 def test_unknown_or_city_job_has_no_invented_boost(self):self.assertIsNone(events_for_job(dict(origin=dict(kind='city')),[]))
 def test_matching_requires_exact_player_target_and_time(self):
  case=dict(origin=dict(kind='boost',target='TECH_A'),case=dict(player=2,first_matching_reservation=dict(turn=45)))
  rows=[dict(player=2,target='TECH_A',turn=44),dict(player=3,target='TECH_A',turn=46),dict(player=2,target='TECH_B',turn=46),dict(player=2,target='TECH_A',turn=47)]
  self.assertEqual(events_for_job(case,rows),[rows[-1]])
 def test_different_loss_classes_in_either_arm_are_retained(self):
  audits=[dict(loss_attribution=dict(cases=[dict(plot=1,prior_resource='SHEEP',classification='district')])),dict(loss_attribution=dict(cases=[dict(plot=1,prior_resource='SHEEP',classification='harvest'),dict(plot=2,prior_resource='CATTLE',classification='harvest')]))]
  values=loss_union(audits);self.assertEqual(len(values),2);self.assertEqual(set(values[0]['losses']),{'control','boost_gate'})
 def test_absent_endpoint_plot_is_missing_not_proven_resource_loss(self):self.assertIsNone(observed_state(None,'SHEEP',[],[],[])['resource_present_at_endpoint'])

if __name__=='__main__':unittest.main()
