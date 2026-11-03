"""Focused synthetic contract checks; native capture is separate evidence."""
import unittest
from copy import deepcopy
from shadow_geometry import review


def fixture():
    tiles=[]
    for p in (10,11,12):
        tiles.append(dict(plot=p, river=p==10, neighbors=[12] if p!=12 else [10,11],
            roles={'BAKERS':dict(base=p==12,specialty=False)},owner=3,resource_visible=True,
            valid_resource_improvement=True,improvement_pillaged=False,district=-1,worked=0))
    candidates=[dict(quarter='BAKERS',plot=p,mapped_customer_types=[dict(type='DISTRICT_TEST_CUSTOMER',index=7)],preview=dict(native={'YIELD_PRODUCTION':1,'YIELD_GOLD':0},
        computed_real={'YIELD_PRODUCTION':p-8},computed_private={'YIELD_CSC_BASE':100}))for p in (10,11)]
    return dict(player=3,city=131073,turn=110,action_authorization=False,execution_readiness='unknown',enrichment_complete=True,tiles=tiles,
        candidates=candidates,chains=[dict(city=99,quarter='TAILORS',plot=20,dependencies=[10])],
        district_state={'BAKERS':dict(targets=[dict(plot=p,legal=True)for p in (10,11)])},
        controls=[dict(city=99,plot=20,preview=dict(native={'YIELD_PRODUCTION':2,'YIELD_GOLD':0}),
            existing_adjacency={'YIELD_PRODUCTION':2,'YIELD_GOLD':0},existing_total={'YIELD_PRODUCTION':99})])


class ShadowTests(unittest.TestCase):
    def test_components_supply_conflict_and_no_action(self):
        raw=fixture();before=deepcopy(raw);v=review(raw,'synthetic')
        self.assertEqual(raw,before);self.assertFalse(v['action_authorization'])
        self.assertEqual(v['execution_readiness'],'unknown');self.assertEqual(len(v['comparisons']),1)
        self.assertTrue(v['opportunities'][0]['materials'][0]['supply_predicate_projection'])
        self.assertEqual(v['conflicts'][0]['kind'],'footprint_on_existing_chain_material')
        self.assertEqual(v['comparisons'][0]['component_delta_first_minus_second']['computed_real']['YIELD_PRODUCTION'],-1)

    def test_unknown_getter_is_partial(self):
        raw=fixture();raw['candidates'][0]['preview']['native']['YIELD_PRODUCTION']={'unavailable':'getter'}
        self.assertEqual(review(raw,'synthetic')['status'],'partial_geometry_no_extension')

    def test_pillage_and_foreign_owner_withhold_supply(self):
        for field,value in [('improvement_pillaged',True),('owner',2),('resource_visible',False),('valid_resource_improvement',False)]:
            raw=fixture();raw['tiles'][2][field]=value
            self.assertFalse(review(raw,'synthetic')['opportunities'][0]['materials'][0]['supply_predicate_projection'])

    def test_complete_native_set_required(self):
        raw=fixture();raw['candidates'].pop()
        with self.assertRaises(ValueError):review(raw,'synthetic')

    def test_zero_candidates_is_a_result(self):
        raw=fixture();raw['candidates']=[];raw['district_state']['BAKERS']['targets']=[]
        v=review(raw,'synthetic');self.assertEqual(v['opportunity_count'],0)
        self.assertEqual(v['status'],'partial_geometry_no_extension')

    def test_bad_identity_or_authority_rejected(self):
        for field,value in [('player',0),('action_authorization',True),('execution_readiness','ready')]:
            raw=fixture();raw[field]=value
            with self.assertRaises(ValueError):review(raw,'synthetic')

    def test_unrelated_adjacent_district_is_not_customer(self):
        raw=fixture();raw['tiles'][2]['district']=23
        v=review(raw,'synthetic')['opportunities'][0]
        self.assertEqual(v['customer_geometry'],[])
        self.assertFalse(v['adjacent_district_geometry'][0]['mapped_customer_match'])
        raw['tiles'][2]['district']=7
        self.assertTrue(review(raw,'synthetic')['opportunities'][0]['customer_geometry'][0]['mapped_customer_match'])

    def test_incomplete_enrichment_never_passes(self):
        raw=fixture();raw['enrichment_complete']=False
        v=review(raw,'synthetic');self.assertTrue(v['native_accessor_positive'])
        self.assertEqual(v['status'],'partial_geometry_no_extension')


if __name__=='__main__':unittest.main()
