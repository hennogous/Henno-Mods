"""Synthetic decision scenarios; not native outcome or tuning evidence."""
import copy
import unittest
from site_evaluator import COSTS, GATES, YIELDS, archive_coverage, current_dominance, evaluate_site


def fact(v):
    return {'value': v, 'source': 'synthetic fixture / observed field'}


def mapping():
    return {'validated': fact(True), 'snapshot': 'fixture enabled mappings',
            'quarter_classes': {'Q': {'base': 'B', 'specialty': 'S'}},
            'TypeTags': [{'Type': 'RESOURCE_OPTIONAL', 'Tag': 'B', 'source': 'TypeTags/0'},
                         {'Type': 'RESOURCE_SECOND', 'Tag': 'S', 'source': 'TypeTags/1'}],
            'Improvement_ValidResources': [{'ResourceType': r, 'ImprovementType': 'I', 'source': 'Improvement_ValidResources/' + r}
                                          for r in ('RESOURCE_OPTIONAL', 'RESOURCE_SECOND')]}


def site(p=2, g=2):
    return {'identity': {'player': 1, 'city': 2, 'turn': 50, 'plot': 10, 'source': 'fixture'}, 'quarter': 'Q',
            **{k: fact(True) for k in GATES}, 'current_real': dict(zip(YIELDS, (fact(p), fact(g)))),
            'river': fact(True), 'current_customers': fact([]), 'built_stages': fact([]),
            'existing_unfinished_chains': fact([]), 'build_commitment': fact('new'),
            'customer_alternatives': fact([]), 'material_inventory_complete': fact(True),
            'costs': {k: fact(0) for k in COSTS},
            'materials': [{'resource': 'RESOURCE_OPTIONAL', 'plot': 11, 'source': 'fixture/material',
                           'adjacent': fact(True), 'supply_eligible': fact(True),
                           'supply_context':fact({'player':1,'city':2,'quarter':'Q'}),
                           'improved_working': fact(True), 'improvement': 'I'}], 'future': []}


def future(plot=12, kind='customer'):
    return {'plot': plot, 'kind': kind, 'source': 'fixture future', **{k: fact(True) for k in GATES},
            'delay_turns': fact(8), 'mapped_customer': fact(True), 'adjacent': fact(True),
            'incremental_real': dict(zip(YIELDS, (fact(0), fact(1)))), 'costs': {k: fact(0) for k in COSTS}}


class EvaluatorTests(unittest.TestCase):
    def evaluate(self, s):
        return evaluate_site(s, mapping())

    def test_bands_strong_marginal_and_infeasible(self):
        for p, g, expected in ((1, 2, '+3'), (2, 2, '+4'), (2, 3, '+5_or_more')):
            self.assertEqual(self.evaluate(site(p, g))['current']['band'], expected)
        self.assertEqual(self.evaluate(site())['recommendation'], 'promising_review')
        self.assertEqual(self.evaluate(site(0, 0))['recommendation'], 'marginal_review')
        s = site(); s['legal'] = fact(False)
        self.assertEqual(self.evaluate(s)['recommendation'], 'infeasible')

    def test_private_yield_never_counts_or_fills_missing(self):
        s = site(); del s['current_real'][YIELDS[1]]
        s['current_real']['YIELD_CSC_AI_PLACEMENT'] = fact(999)
        r = self.evaluate(s)
        self.assertIsNone(r['current'][YIELDS[1]])
        self.assertEqual(r['current']['band'], 'unknown')
        self.assertEqual(r['recommendation'], 'insufficient_evidence')

    def test_current_and_future_do_not_merge(self):
        s = site(1, 1); s['future'] = [future()]
        r = self.evaluate(s)
        self.assertEqual(r['current']['band'], 'below_+3')
        self.assertEqual(r['projected_band'], '+3')
        self.assertEqual(r['future'][0]['status'], 'credible_conditional')

    def test_unavailable_capacity_and_unknown_access_withhold(self):
        for gate, v in (('capacity_supported', False), ('accessible', None), ('affordable', None)):
            s = site(); plan = future(); plan[gate] = fact(v); s['future'] = [plan]
            r = self.evaluate(s)
            self.assertIsNone(r['future'][0]['incremental_real'])
            self.assertEqual(r['credible_future_increment'][YIELDS[1]], 0)
            self.assertEqual(r['recommendation'], 'insufficient_evidence')

    def test_conflicting_future_plot(self):
        s = site(); s['future'] = [future(), future()]
        r = self.evaluate(s)
        self.assertIn('conflicting future plot', r['future'][1]['issues'])
        self.assertEqual(r['credible_future_increment'][YIELDS[1]], 0)
        self.assertIsNone(r['future_total_increment'])

    def test_lost_base_not_counted_as_supply(self):
        s = site(); s['materials'][0]['plot'] = 10
        r = self.evaluate(s)
        self.assertEqual(r['current_supply'], [])
        self.assertEqual(len(r['material_footprint_loss']), 1)
        self.assertEqual(r['recommendation'], 'tradeoff_review')

    def test_unrelated_mod_resource_no_proxy_credit(self):
        s = site(); s['materials'][0]['resource'] = 'RESOURCE_UNRELATED_MOD'
        r = self.evaluate(s)
        self.assertEqual(r['materials'][0]['state'], 'unrelated')
        self.assertEqual(r['recommendation'], 'marginal_no_mapped_base')

    def test_footprint_loss_to_another_quarter(self):
        m = mapping(); m['quarter_classes']['OTHER'] = {'base': 'OTHER_B', 'specialty': 'OTHER_S'}
        m['TypeTags'].append({'Type': 'RESOURCE_OTHER', 'Tag': 'OTHER_B', 'source': 'TypeTags/2'})
        s = site(); s['materials'].append({'resource': 'RESOURCE_OTHER', 'plot': 10, 'source': 'fixture other supply'})
        r = evaluate_site(s, m)
        self.assertEqual(r['material_footprint_loss'][0]['affected_roles'], [{'quarter':'OTHER', 'role':'base'}])
        self.assertEqual(r['recommendation'], 'tradeoff_review')

    def test_validated_mapping_required(self):
        m = mapping(); m['validated'] = fact(False)
        with self.assertRaises(ValueError): evaluate_site(site(), m)
        m = mapping(); del m['TypeTags'][0]['source']
        with self.assertRaises(ValueError): evaluate_site(site(), m)

    def test_both_future_is_not_service_or_current_supply(self):
        s = site(0, 0); f = future(kind='material')
        f.update(resource='RESOURCE_SECOND', improvement='I', adjacent=fact(True))
        s['materials'].append({'plot':12, 'resource':'RESOURCE_SECOND', 'source':'fixture observed resource', 'adjacent':fact(True), 'improved_working':fact(False)})
        s['future'] = [f]
        r = self.evaluate(s)
        self.assertFalse(r['both_service_potential']['current_mapped_supply'])
        self.assertTrue(r['both_service_potential']['with_credible_development'])
        self.assertIsNone(r['both_service_potential']['active_service'])
        self.assertEqual(r['recommendation'], 'promising_review')

    def test_customer_alternative_and_unfinished_chains_require_review(self):
        for field in ('customer_alternatives', 'existing_unfinished_chains'):
            s = site(); s[field] = fact([{'plot': 99, 'reason': 'valuable alternative'}])
            self.assertEqual(self.evaluate(s)['recommendation'], 'tradeoff_review')

    def test_unknown_cost_not_free(self):
        s = site(); del s['costs']['acquisition_gold']
        self.assertIsNone(self.evaluate(s)['costs']['acquisition_gold'])
        s = site(); f = future(); del f['costs']['builder_charges']; s['future'] = [f]
        self.assertEqual(self.evaluate(s)['future'][0]['status'], 'withheld')

    def test_dominance_requires_same_context_and_complete_costs(self):
        a, b = site(3, 2), site(2, 2)
        self.assertEqual(current_dominance(self.evaluate(a), self.evaluate(b)), 'a_current_vector_dominates')
        a['costs']['production'] = fact(10)
        self.assertEqual(current_dominance(self.evaluate(a), self.evaluate(b)), 'no_dominance')
        del b['costs']['travel_turns']
        self.assertEqual(current_dominance(self.evaluate(a), self.evaluate(b)), 'undetermined')

    def test_no_input_mutation(self):
        s = site(); before = copy.deepcopy(s); self.evaluate(s)
        self.assertEqual(s, before)

    def test_footprint_loss_does_not_require_self_adjacency(self):
        s = site(); s['materials'][0].update(plot=10, adjacent=fact(False))
        r = self.evaluate(s)
        self.assertEqual(r['materials'][0]['state'], 'lost_to_footprint')
        self.assertEqual(r['current_supply'], [])
        self.assertTrue(r['material_footprint_loss'])

    def test_current_supply_requires_native_bound_eligibility(self):
        for eligible in (False, None):
            s = site(); s['materials'][0]['supply_eligible'] = fact(eligible)
            r = self.evaluate(s)
            self.assertEqual(r['current_supply'], [])
        s = site(); del s['materials'][0]['supply_eligible']
        self.assertEqual(self.evaluate(s)['recommendation'], 'insufficient_evidence')
        s = site(); s['materials'][0]['supply_context'] = fact({'player':9,'city':2,'quarter':'Q'})
        self.assertEqual(self.evaluate(s)['current_supply'], [])

    def test_remote_customer_withheld(self):
        s = site(); f = future(); f['adjacent'] = fact(False); s['future'] = [f]
        self.assertEqual(self.evaluate(s)['future'][0]['status'], 'withheld')

    def test_future_material_cannot_invent_resource(self):
        s = site(); f = future(kind='material'); f.update(resource='RESOURCE_SECOND', improvement='I')
        s['future'] = [f]
        r = self.evaluate(s)
        self.assertEqual(r['future'][0]['status'], 'withheld')
        self.assertFalse(r['both_service_potential']['with_credible_development'])

    def test_missing_identity_never_promising(self):
        for field in ('player', 'city', 'turn', 'plot'):
            s = site(); s['identity'][field] = None
            self.assertEqual(self.evaluate(s)['recommendation'], 'insufficient_evidence')

    def test_unknown_improvement_is_not_assumed_unimproved(self):
        s = site(); del s['materials'][0]['improved_working']
        self.assertEqual(self.evaluate(s)['recommendation'], 'insufficient_evidence')

    def test_pareto_context_values_ignore_source_pointer(self):
        a,b = site(3,2),site(2,2)
        for key in ('river','built_stages','current_customers','build_commitment'):
            b[key]['source'] = 'different legitimate JSON pointer'
        self.assertEqual(current_dominance(self.evaluate(a), self.evaluate(b)), 'a_current_vector_dominates')


if __name__ == '__main__': unittest.main()
