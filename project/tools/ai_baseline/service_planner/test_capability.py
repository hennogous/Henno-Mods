"""Unavailable command authority must not suppress legal owned-land work."""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from .policy import Planner,Policy,Budget
from .observations import build_candidates
from .test_material import observation
from .coordinator import Coordinator

class CapabilityTests(unittest.TestCase):
 def setUp(self):
  self.buy=build_candidates(observation(),material_first=True,stepwise=True)[0]
  self.place=replace(self.buy,quarter='BAKERS',plot=43,base=2,specialty=0,
    source_owned=True,owned_base=2,owned_specialty=0,current_legal=True,
    missing_tiles=(),purchase_plot=None,material_plots=(83,),plan_materials=(83,))
 def test_unavailable_purchase_does_not_consume_city_choice(self):
  p=Planner(Policy.material_first_v2());p.update(1,10,60,[self.buy,self.place])
  out=p.select({}, {1:Budget(600,10)},60,lambda c:c,allowed_actions={'place'})
  self.assertEqual([d.action for d in out],['place'])
  self.assertEqual([d.action for d in p.unavailable_decisions],['purchase'])
 def test_default_retains_purchase_priority(self):
  p=Planner(Policy.material_first_v2());p.update(1,10,60,[self.buy,self.place])
  self.assertEqual(p.select({}, {1:Budget(600,10)},60,lambda c:c)[0].action,'purchase')
  self.assertFalse(p.unavailable_decisions)
 def adapter(self):
  from types import SimpleNamespace
  def result(c):
   return dict(verified=True,owner=c.player,plot=c.plot,quarter=c.quarter,
    progress_before=0,progress_after=0,cost_before=30,cost_after=30,native_incomplete=True,queue_unchanged=True)
  return SimpleNamespace(wide_candidates=lambda *a:[self.buy,self.place],refresh=lambda c:c,
   needs=lambda *a:{},budget=lambda *a:Budget(600,10),place_zero=result,
   purchase_facts=lambda *a:(_ for _ in ()).throw(AssertionError('Unavailable purchase must not enter preflight')))
 def test_real_coordinator_defers_without_pending_but_places_alternative(self):
  with TemporaryDirectory(dir=Path.cwd())as t:
   c=Coordinator(None,Path(t)/'journal',allow_mutations=True,boundary=lambda:{'turn':60,'autoplay_active':False},
      policy=Policy.material_first_v2(),purchase_capability={'available':False,'evidence':'native receipt unchanged'})
   out=c.cycle(1,[10],60,self.adapter())
   self.assertEqual([r['action']for r in out],['purchase_unavailable','foundation_confirmed'])
   self.assertFalse(c.executor.pending);self.assertFalse(c.executor.authority_probe_used)
   events=(Path(t)/'journal').read_text()
   self.assertIn('foundation-confirmed',events);self.assertNotIn('purchase-begin',events)
 def test_readonly_preview_keeps_unavailable_purchase_as_proposal(self):
  with TemporaryDirectory(dir=Path.cwd())as t:
   c=Coordinator(None,Path(t)/'journal',allow_mutations=False,policy=Policy.material_first_v2(),purchase_capability={'available':False})
   out=c.cycle(1,[10],60,self.adapter())
   self.assertEqual(out[0]['action'],'proposal');self.assertEqual(out[0]['decision'].action,'purchase')
   self.assertFalse((Path(t)/'journal').exists())

if __name__=='__main__':unittest.main()
