import unittest
from copy import deepcopy
from selective_planner import shortlist
from test_site_evaluator import site as evaluator_site, mapping, future, fact


def site(*args):
    return dict(evaluator_site(*args), configured_ai=fact(True))


class SelectiveTests(unittest.TestCase):
    def status(self,s):
        return shortlist([s],mapping())['alternatives'][0]['status']

    def test_plus_three_is_not_plus_four_default(self):
        self.assertEqual(self.status(site(2,1)), 'decline_below_trial_threshold')
        self.assertEqual(self.status(site(2,2)), 'shortlisted_for_investment_review')

    def test_both_option_can_qualify_below_four(self):
        s=site(1,1);s['materials'].append(dict(s['materials'][0],plot=12,resource='RESOURCE_SECOND'))
        self.assertEqual(self.status(s),'shortlisted_for_investment_review')

    def test_no_base_even_high_adjacency_is_declined(self):
        s=site(5,5);s['materials']=[]
        self.assertEqual(self.status(s),'decline_no_credible_base')

    def test_credible_future_counts_but_unsupported_future_does_not(self):
        s=site(2,1);s['future']=[future()]
        self.assertEqual(self.status(s),'shortlisted_for_investment_review')
        s['future'][0]['capacity_supported']=fact(None)
        self.assertEqual(self.status(s),'defer_missing_evidence')

    def test_customer_alternative_and_existing_chain_need_comparison(self):
        for field in ('existing_unfinished_chains','customer_alternatives'):
            s=site();s[field]=fact(['better option to compare'])
            self.assertEqual(self.status(s),'compare_existing_commitments_or_displacement')
        s=site();s['build_commitment']=fact('accepted_waiting')
        self.assertEqual(self.status(s),'compare_existing_commitments_or_displacement')

    def test_missing_price_is_not_zero(self):
        s=site();s['costs']['acquisition_gold']=fact(None)
        self.assertEqual(self.status(s),'defer_missing_evidence')

    def test_original_human_and_unknown_role_are_not_shortlisted(self):
        s=site();s['configured_ai']=fact(False)
        self.assertEqual(self.status(s),'excluded_original_human')
        del s['configured_ai']
        self.assertEqual(self.status(s),'defer_missing_evidence')

    def test_only_same_context_dominated_sites_removed_no_budget_authority(self):
        a=site(3,2);b=site(2,2);b['identity']['plot']=20
        before=deepcopy([a,b]);result=shortlist([a,b],mapping())
        self.assertEqual([r['status'] for r in result['alternatives']],
                         ['shortlisted_for_investment_review','dominated_same_context'])
        self.assertFalse(result['action_authorization']);self.assertEqual([a,b],before)

    def test_different_material_and_customer_context_is_not_dominated(self):
        a=site(3,2);b=site(2,2);b['identity']['plot']=20;b['current_customers']=fact(['harbor'])
        self.assertEqual(len(shortlist([a,b],mapping())['shortlist']),2)

    def test_duplicate_or_mixed_scope_rejected(self):
        with self.assertRaises(ValueError):shortlist([site(),site()],mapping())
        a=site();b=site();b['identity']['turn']=51
        with self.assertRaises(ValueError):shortlist([a,b],mapping())


if __name__=='__main__':unittest.main()
