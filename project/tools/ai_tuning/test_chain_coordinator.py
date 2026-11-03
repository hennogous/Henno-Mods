import copy
import unittest

from chain_coordinator import coordinate
from test_site_evaluator import fact, mapping, site, future


def chain(plot=40, dependency=10):
    return {'identity': {'player': 1, 'city': 2, 'turn': 50, 'plot': plot, 'source': 'fixture/chain'},
            'quarter': 'Q2', 'state': fact('unfinished'), 'request_state': fact('accepted_waiting'),
            'remaining_production': fact(12),
            'material_dependencies': [{'plot': dependency, 'native_bound': fact(True)}]}


def snapshot(sites=None, chains=None):
    return {'source': 'fixture/snapshot', 'player': 1, 'turn': 50, 'mapping': mapping(),
            'production_capacity': fact(None), 'sites': sites if sites is not None else [site()],
            'chains': chains if chains is not None else []}


class CoordinatorTests(unittest.TestCase):
    def test_exclusive_footprints_and_future_conflicts_are_order_independent(self):
        a, b = site(), site(); b['quarter'] = 'Q'; b['identity']['city'] = 3
        # Different identities but the same exact footprint.
        a['future'] = [future(12, 'material')]; b['future'] = [future(12, 'material')]
        s = snapshot([a, b]); first = coordinate(s)
        s['sites'].reverse(); second = coordinate(s)
        self.assertEqual(first, second)
        self.assertEqual({(r['kind'], r['status']) for r in first['site_relationships']},
                         {('footprint', 'incompatible'), ('future_material', 'conditional_unresolved')})
        self.assertFalse(first['action_authorization'])
        self.assertEqual(first['joint_allocation'], 'deferred')

    def test_footprint_over_other_chain_dependency_is_a_tradeoff_not_ban(self):
        result = coordinate(snapshot(chains=[chain()]))
        dep = result['chain_dependencies'][0]
        self.assertEqual(dep['kind'], 'material_dependency_tradeoff')
        self.assertIsNone(dep['loss_value'])
        self.assertEqual(result['options'][0]['status'], 'review')
        self.assertFalse(result['action_authorization'])

    def test_accepted_waiting_high_score_unknown_capacity_is_not_finish_first(self):
        high = site(9, 9)
        out = coordinate(snapshot([high], [chain(dependency=20)]))
        self.assertEqual(out['site_evidence'][0]['evidence']['current']['band'], '+5_or_more')
        finish = next(x for x in out['options'] if x['kind'] == 'finish')
        self.assertEqual(finish['request_state']['value'], 'accepted_waiting')
        self.assertEqual(out['preference'], 'deferred')
        self.assertIsNone(out['production_capacity']['value'])
        self.assertTrue(any('capacity unknown' in u for u in out['unknowns']))

    def test_shared_customer_unknown_then_proved(self):
        a, b = site(), site(); b['identity']['plot'] = 20
        a['future'] = [future(12)]; b['future'] = [future(12)]
        s = snapshot([b, a]); out = coordinate(s)
        self.assertEqual(out['site_relationships'][0]['status'], 'unresolved')
        refs = [{'city': 2, 'quarter': 'Q', 'plot': x} for x in (20, 10)]
        s['customer_sharing'] = [{'sites': refs, 'plot': 12, 'shareable': fact(True)}]
        self.assertEqual(coordinate(s)['site_relationships'][0]['status'], 'shareable_with_proof')
        s['customer_sharing'][0]['shareable'] = fact(False)
        self.assertEqual(coordinate(s)['site_relationships'][0]['status'], 'incompatible_with_proof')

    def test_invalid_identity_evidence_and_enums_fail_closed(self):
        cases = []
        for field, val in [('turn', 49), ('player', 9), ('city', True)]:
            s = snapshot(); s['sites'][0]['identity'][field] = val; cases.append(s)
        s = snapshot(); s['source'] = ''; cases.append(s)
        s = snapshot(chains=[chain()]); s['chains'][0]['request_state'] = fact('pending'); cases.append(s)
        s = snapshot(chains=[chain()]); s['chains'][0]['state'] = {'value': 'unfinished'}; cases.append(s)
        s = snapshot(chains=[chain()]); s['chains'][0]['material_dependencies'][0]['native_bound'] = fact(1); cases.append(s)
        s = snapshot(chains=[chain()]); s['chains'][0]['remaining_production'] = fact(True); cases.append(s)
        s = snapshot(); s['mapping']['validated'] = fact(False); cases.append(s)
        for s in cases:
            with self.subTest(s=s), self.assertRaises(ValueError): coordinate(s)

    def test_infeasible_site_is_ineligible_and_reasons_visible(self):
        candidate = site(); candidate['legal'] = fact(False)
        out = coordinate(snapshot([candidate]))
        start = out['options'][0]
        self.assertEqual(start['status'], 'ineligible')
        self.assertTrue(start['needs_site_review'])
        self.assertIn('site legal', start['rejections'])
        candidate['legal'] = fact(None)
        start = coordinate(snapshot([candidate]))['options'][0]
        self.assertEqual(start['status'], 'deferred')
        self.assertIn('site legal', start['unknowns'])

    def test_withheld_future_conflict_is_conditional_but_footprint_is_definitive(self):
        a, b = site(), site(); b['identity']['city'] = 3
        a['future'] = [future(12)]; b['future'] = [future(12)]
        a['future'][0]['legal'] = fact(False)
        s = snapshot([a, b]); result = coordinate(s)
        physical = next(x for x in result['site_relationships'] if x['kind'] == 'footprint')
        future_rel = next(x for x in result['site_relationships'] if x['kind'] == 'future_customer')
        self.assertEqual(physical['status'], 'incompatible')
        self.assertEqual(future_rel['status'], 'conditional_unresolved')
        self.assertEqual(future_rel['plan_statuses'], ['withheld', 'credible_conditional'])
        self.assertFalse(future_rel['future_feasibility_established'])
        s['sites'].reverse()
        self.assertEqual(result, coordinate(s))
        refs = [{'city': x['identity']['city'], 'quarter': 'Q', 'plot': 10} for x in (a, b)]
        s['customer_sharing'] = [{'sites': refs, 'plot': 12, 'shareable': fact(True)}]
        relation = next(x for x in coordinate(s)['site_relationships'] if x['kind'] == 'future_customer')
        self.assertEqual(relation['status'], 'conditional_unresolved')
        self.assertEqual(relation['status_if_feasible'], 'shareable_with_proof')
        self.assertEqual(relation['sharing_evidence'], fact(True))

    def test_source_and_output_are_independent(self):
        original = snapshot(chains=[chain()]); saved = copy.deepcopy(original)
        out = coordinate(original)
        self.assertEqual(original, saved)
        out['chains'][0]['request_state']['value'] = 'selected'
        out['site_evidence'][0]['evidence']['provenance']['identity']['plot'] = 999
        self.assertEqual(original, saved)


class ExistingFootprintTests(unittest.TestCase):
    def test_duplicate_start_is_deferred_without_inventing_replacement_policy(self):
        current = chain(plot=10, dependency=20)
        result = coordinate(snapshot(chains=[current]))
        start = next(o for o in result['options'] if o['kind'] == 'start')
        self.assertEqual(start['status'], 'deferred')
        self.assertTrue(start['needs_site_review'])
        self.assertEqual(start['existing_footprints'][0]['plot'], 10)
        self.assertTrue(any(o['kind'] == 'finish' for o in result['options']))
        self.assertFalse(result['action_authorization'])


if __name__ == '__main__':
    unittest.main()
