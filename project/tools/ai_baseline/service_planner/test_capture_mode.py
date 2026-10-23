"""Capture integration must not suppress per-turn planner actions or receipts."""
import unittest
from types import SimpleNamespace
from .capture_mode import CaptureSchedule,evaluate_boundary

class RecordingTests(unittest.TestCase):
 def fixture(self):
  events=[]
  a=SimpleNamespace(r=object(),collect=lambda t:events.append(('fresh',t)),record_chain_metrics=lambda t,**kw:events.append(('metrics',t)))
  e=SimpleNamespace(cycle=lambda a,t:events.append(('action',t)))
  def capture(r,root,write,t):
   events.append(('census',t));return {'chain':{'turn':t}}
  return a,e,capture,events
 def test_light_cycles_every_turn_but_only_one_post_action_snapshot(self):
  a,e,capture,events=self.fixture()
  for t in range(114,127):evaluate_boundary(a,e,t,None,None,capture_bundle=capture)
  self.assertEqual([t for k,t in events if k=='fresh'],list(range(114,127)))
  self.assertEqual([t for k,t in events if k=='action'],list(range(114,127)))
  self.assertEqual([t for k,t in events if k=='census'],[125])
  self.assertLess(events.index(('action',125)),events.index(('census',125)))
 def test_endpoint_records_without_placing_or_purchasing(self):
  a,e,capture,events=self.fixture();evaluate_boundary(a,e,250,None,None,capture_bundle=capture)
  self.assertEqual(events,[('fresh',250),('census',250),('metrics',250)])
 def test_deep_mode_is_explicit_and_does_not_change_actions(self):
  a,e,capture,events=self.fixture();evaluate_boundary(a,e,114,None,None,schedule=CaptureSchedule('deep'),capture_bundle=capture)
  self.assertEqual(events,[('fresh',114),('action',114),('census',114),('metrics',114)])
