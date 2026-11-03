import json,unittest
from pathlib import Path
from material_signal_delivery import summarize_domain,report
class Delivery(unittest.TestCase):
    def rows(self,c,n):return [dict(owned_control_delta=c,newly_acquired_delta=n)for i in range(6)]
    def test_no_positive_control_never_declares_missing_delivery(self):
        r=summarize_domain(self.rows(0,0));self.assertEqual(r['state'],'no_consistent_positive_control');self.assertFalse(r['acquired_delivery_comparison_informative'])
    def test_missing_control_records_not_zero(self):
        r=summarize_domain([]);self.assertEqual(r['state'],'incomplete_or_missing_observations')
        r=summarize_domain([dict(owned_control_delta=80,newly_acquired_delta=None)]*6);self.assertFalse(r['positive_control_verified'])
    def test_positive_control_bought_zero(self):
        r=summarize_domain(self.rows(80,0));self.assertEqual(r['state'],'acquired_response_absent_with_positive_control');self.assertFalse(r['ownership_registration_cause_proven'])
    def test_both_respond_is_not_AI_consumption(self):
        r=summarize_domain(self.rows(80,80));self.assertEqual(r['state'],'acquired_response_matches_positive_control');self.assertFalse(r['native_AI_consumption_proven'])
    def test_mixed_not_success(self):
        rows=self.rows(80,80);rows[0]['newly_acquired_delta']=0
        self.assertEqual(summarize_domain(rows)['state'],'mixed_acquired_response')
    def test_actual_native_audit_domains_separate(self):
        p=Path('C:/Users/Shadow/Desktop/Codex/csc-material-care-v2-20261023/acquisition-signal-delivery16-probe-v2/independent-signal-delivery-audit.json');r=report(json.loads(p.read_text()))
        self.assertEqual(r['domains']['Core']['state'],'no_consistent_positive_control')
        self.assertEqual(r['domains']['UI']['state'],'acquired_response_absent_with_positive_control')
if __name__=='__main__':unittest.main()
