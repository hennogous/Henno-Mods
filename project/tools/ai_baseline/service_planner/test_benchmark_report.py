import unittest
from .benchmark_report import report_points

def site(player=1):return dict(player=player,plot=42,quarter='TAILORS',complete=True,pillaged=False,producer_built=True,owned_base=1,owned_spec=0,improved_base=1,materials=[dict(plot=81,category='base',resource='WOOL',owner=player,improvement='PASTURE',pillaged=False)])
def point(t=100,s=None):return dict(turn=t,sites=[site()]if s is None else s,yields={'YIELD_PRODUCTION':10,'YIELD_CSC_AI_PLACEMENT':500})
class ReportTests(unittest.TestCase):
 def test_private_signal_not_economic_output(self):
  r=report_points([point()],[]);self.assertEqual(r['economic_yields'],{'YIELD_PRODUCTION':10});self.assertEqual(r['private_AI_signals_excluded']['YIELD_CSC_AI_PLACEMENT'],500)
 def test_capture_stays_assisted(self):
  r=report_points([point(s=[site(2)])],[dict(player=1,plot=42,quarter='TAILORS')]);self.assertEqual(r['groups']['assisted']['current_AI_quarters'],1)
 def test_missing_target_not_destroyed(self):
  r=report_points([point(s=[])],[dict(plot=42,quarter='TAILORS')]);self.assertEqual(r['assisted_targets_not_in_current_AI_census'],1);self.assertNotIn('destroyed_count',r)
 def test_zero_denominator_not_false_zero(self):
  r=report_points([point(s=[])],[]);self.assertIsNone(r['observed_material_link_retention']['value'])
 def test_duplicate_turn_rejected(self):
  with self.assertRaisesRegex(AssertionError,'Duplicate'):report_points([point(),point()],[])
 def test_repair_not_uninterrupted_preservation(self):
  middle=site();middle['materials'][0]['pillaged']=True;r=report_points([point(100),point(101,[middle]),point(102)],[]);self.assertEqual(r['observed_material_link_retention']['value'],1);self.assertEqual(r['material_links_available_at_every_observed_checkpoint']['value'],0)
 def test_coverage_gaps_explicit(self):self.assertEqual(report_points([point(100),point(102)],[])['coverage']['missing_turns'],[101])
 def test_absent_observations_rejected(self):
  with self.assertRaisesRegex(AssertionError,'No observations'):report_points([],[])
if __name__=='__main__':unittest.main()
