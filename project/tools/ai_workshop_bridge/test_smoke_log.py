"""Regression for receipts emitted before per-turn publication resets counters."""
import json
from pathlib import Path
import tempfile
import unittest
from run_smoke import log_delivery

class LogDeliveryTests(unittest.TestCase):
    def analyze(self,rows):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'Lua.log'
            p.write_text('\n'.join('CSC_AI_WorkshopBridge: CSC_WORKSHOP_BRIDGE turn '+json.dumps(r)for r in rows),encoding='utf-8')
            return log_delivery(p,256)
    def test_retains_largest_receipt_before_counter_reset(self):
        base=dict(generation=7,changed=1,faults=0,samples=[[1,65536,36,2755,1982,2238]])
        larger=dict(base,changed=2,samples=base['samples']+[[2,65536,36,2178,3166,3422]])
        other=dict(base,generation=9)
        result=self.analyze([base,larger,larger,dict(base,changed=0,samples=[]),other])
        self.assertEqual(result['observed_adjustments'],3)
        self.assertEqual(len(result['windows']),2)
    def test_rejects_original_human_receipt(self):
        with self.assertRaises(RuntimeError):self.analyze([dict(generation=1,changed=1,faults=0,samples=[[0,1,36,1,2,258]])])
    def test_rejects_wrong_delta(self):
        with self.assertRaises(RuntimeError):self.analyze([dict(generation=1,changed=1,faults=0,samples=[[1,1,36,1,2,259]])])
    def test_rejects_native_fault(self):
        with self.assertRaises(RuntimeError):self.analyze([dict(generation=1,changed=1,faults=1,samples=[])])

if __name__=='__main__':unittest.main()
