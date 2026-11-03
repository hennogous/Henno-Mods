"""Decision/host-interface tests. Fixtures are synthetic, not native evidence."""
import unittest
from copy import deepcopy
from pathlib import Path
from investment_review import review, preview_host
from test_site_evaluator import fact, site, future
from test_chain_coordinator import snapshot, chain

POLICY=Path(__file__).resolve().parents[3]/'Civ Supply Chains/Lua_UI/AI/CSC_AI_OpportunityPolicy.lua'

def ready():
    s=site();s['configured_ai']=fact(True)
    s['materials'].append(dict(s['materials'][0],plot=12,resource='RESOURCE_SECOND'))
    data=snapshot([s]);data['production_capacity']=fact(10)
    return data

def finance(subsidies=True):
    return {k:fact(v)for k,v in dict(gold=72.39453125,gross=7.19921875,upkeep=0,spent=25,subsidies=subsidies).items()}

def tiles():
    return {10:dict(owner=2,neighbors=[11],source='fixture owned anchor'),
            11:dict(owner=-1,neighbors=[10],reach=True,price=40,source='fixture quote')}

class ReviewTests(unittest.TestCase):
    def test_single_ready_both_yields_host_shape_without_action_authority(self):
        data=ready();before=deepcopy(data);r=review(data)
        self.assertEqual(r['decision'],'review_start_with_guarded_host')
        self.assertEqual(r['proposed_host_candidate'],dict(player=1,city=2,quarter='Q',source=10,materials=[11,12],turn=50))
        self.assertFalse(r['action_authorization']);self.assertEqual(r['native_calls'],0);self.assertEqual(data,before)

    def test_plus4_without_specialty_is_explicit_host_gap(self):
        data=ready();data['sites'][0]['materials'].pop()
        self.assertEqual(review(data)['decision'],'defer_unsupported_host_route')

    def test_credible_material_development_not_backdated_or_double_counted(self):
        data=ready();data['sites'][0]['materials'][1]['improved_working']=fact(False)
        plan=future(12,'material');plan.update(resource='RESOURCE_SECOND',improvement='I')
        plan['incremental_real']={'YIELD_PRODUCTION':fact(0),'YIELD_GOLD':fact(0)}
        plan['costs']['builder_charges']=fact(1);data['sites'][0]['future']=[plan]
        r=review(data);self.assertEqual(r['decision'],'review_start_with_guarded_host')
        self.assertEqual(r['proposed_host_candidate']['materials'],[11,12])
        self.assertEqual(r['starts']['alternatives'][0]['evaluation']['credible_future_increment']['YIELD_GOLD'],0)
        self.assertFalse(r['action_authorization'])

    def test_accepted_native_commitment_observed_not_duplicated(self):
        data=ready();data['chains']=[chain(dependency=20)]
        r=review(data);self.assertEqual(r['decision'],'respect_existing_native_commitment')
        self.assertIsNone(r['proposed_host_candidate']);self.assertEqual(r['spending'],0)

    def test_completed_existing_footprint_is_not_a_new_start(self):
        data=ready();c=chain(plot=10,dependency=20);c['state']=fact('complete');c['request_state']=fact('no_request');data['chains']=[c]
        self.assertEqual(review(data)['decision'],'defer_investment')

    def test_unknown_cost_or_original_human_blocks_start(self):
        for key in('cost','human'):
            data=ready()
            if key=='cost':data['sites'][0]['costs']['production']=fact(None)
            else:data['sites'][0]['configured_ai']=fact(False)
            self.assertIsNone(review(data)['proposed_host_candidate'])

    def test_actual_lua_funding_and_opt_out(self):
        r=preview_host(POLICY,player=2,required=[10,11],tiles=tiles(),finance=finance())
        self.assertEqual(r['route'],[11]);self.assertEqual(r['next_tile_funding']['own'],37)
        self.assertEqual(r['next_tile_funding']['grant'],3);self.assertFalse(r['action_authorization'])
        self.assertIsNone(preview_host(POLICY,player=2,required=[10,11],tiles=tiles(),finance=finance(False))['next_tile_funding'])

    def test_unknown_treasury_is_not_zero_and_foreign_route_rejected(self):
        f=finance();f['gold']=fact(None)
        self.assertIn('gold',preview_host(POLICY,player=2,required=[10,11],tiles=tiles(),finance=f)['unknown_finance'])
        data=tiles();data[11]['owner']=3
        with self.assertRaises(ValueError):preview_host(POLICY,player=2,required=[10,11],tiles=data,finance=finance())

    def test_actual_cap_guard_and_already_owned_empty_route(self):
        f=finance();f['spent']=fact(280)
        self.assertIsNone(preview_host(POLICY,player=2,required=[10,11],tiles=tiles(),finance=f)['next_tile_funding'])
        data=tiles();data[11]['owner']=2
        self.assertEqual(preview_host(POLICY,player=2,required=[10,11],tiles=data,finance={})['route'],[])

if __name__=='__main__':unittest.main()
