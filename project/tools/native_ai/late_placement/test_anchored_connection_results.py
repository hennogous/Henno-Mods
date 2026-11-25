import hashlib
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from anchored_connection_results import (anchored_target_results, bid_competition, common_layout_conversion, common_layout_report,
                                         completed_substitute_pairs, connection_counts, customer_land_purchases, endpoint_pair_facts,
                                         endpoint_pair_supply, failed_district_requests, loadable_layout_endpoint,
                                         prospective_footprint_counts, prospective_footprints, prospective_layouts,
                                         supplier_history, wonder_connections)
from paired_layout_replay_results import trace_arm
from planning_results import parse


def record(kind, **fields):
    return f'CSC_PLANNING_{kind}\t' + '\t'.join(f'{k}={v}' for k, v in fields.items())


def relation(player, quarter, qplot, customer, turn, first, **state):
    common = dict(player=player, quarter=quarter, quarterPlot=qplot, neighbourPlot=customer,
                  role='customer', present='true', quarterComplete='true', neighbourComplete='true',
                  foundationOrder=first, quarterFoundationTurn=4 if first == 'quarterFirst' else 9,
                  neighbourFoundationTurn=9 if first == 'quarterFirst' else 4, neighbourDistrict=6, turn=turn)
    return record('RELATION', **(common | state))


class ConnectionCounts(unittest.TestCase):
    def test_named_autosave_survives_slot_rotation_and_preserves_player_edits(self):
        with TemporaryDirectory() as temp:
            root=Path(temp)/'arm'
            archive=root/'endpoint-autosave/source-250.Civ6Save'
            archive.parent.mkdir(parents=True)
            source=Path(temp)/'Single/auto/AutoSave_0250.Civ6Save'
            source.parent.mkdir(parents=True)
            archive.write_bytes(b'first game at turn 250')
            source.write_bytes(b'rotated slot')
            digest=hashlib.sha256(archive.read_bytes()).hexdigest()
            receipt=dict(archive=str(archive),source=str(source),status='archived',turn=250,verified_turn=250,
                         native_closed_verified=True,size=archive.stat().st_size,sha256=digest)
            (root/'completed-via-autosave.json').write_text(json.dumps(receipt),encoding='utf-8')
            native=Path(loadable_layout_endpoint(root,42,'treatment'))
            self.assertEqual(native.parent,source.parent.parent)
            self.assertEqual(native.read_bytes(),archive.read_bytes())
            self.assertEqual(loadable_layout_endpoint(root,42,'treatment'),str(native))
            native.write_bytes(b'player edits')
            with self.assertRaisesRegex(ValueError,'differs'):
                loadable_layout_endpoint(root,42,'treatment')
            self.assertEqual(native.read_bytes(),b'player edits')
            self.assertEqual(archive.read_bytes(),b'first game at turn 250')

    def test_sales_pairs_and_checkpoint_build_order_agree_with_the_endpoint(self):
        census={'turn':20, 'rows':[('QUARTER','BAKERS\t1\t7\t10\ttrue\tfalse')]}
        row=dict(kind='RELATION',turn=13,player=1,city=7,quarter='BAKERS',quarterPlot=10,
                 neighbourDistrict=6,neighbourCity=7,role='sales',present=True,quarterComplete=True,
                 neighbourComplete=True,neighbourPillaged=False,quarterFirstSeen=10,neighbourFirstSeen=13)
        earlier=row | dict(neighbourPlot=20,neighbourFoundationTurn=13,foundationOrder='quarterPreexistingDateUnknown')
        uncertain=row | dict(neighbourPlot=21,quarterFoundationTurn=13,foundationOrder='neighbourPreexistingDateUnknown')
        simultaneous=row | dict(neighbourPlot=22,foundationOrder='sameTurn')
        observed=[earlier,earlier | dict(role='customer'),uncertain,simultaneous]
        counts=connection_counts('',{1},20,observations=observed)
        self.assertEqual(counts['completed_physical_pairs'],{'quarterFirst:BAKERS':1,'unknown:BAKERS':1,'sameTurn:BAKERS':1})
        self.assertEqual(endpoint_pair_supply(census,observed,{1}),{
            'BAKERS:customer:quarterFirst':dict(completed=1,mapped_buyer_district=1),
            'BAKERS:customer:unknown':dict(completed=1,sales_only_district=1),
            'BAKERS:customer:sameTurn':dict(completed=1,sales_only_district=1)})

    def test_completed_pairs_need_their_own_working_base_at_the_endpoint(self):
        census = {'turn': 15, 'rows': [
            ('QUARTER', 'TAILORS\t1\t7\t10\ttrue\tfalse'),
            ('QUARTER', 'BAKERS\t1\t8\t38\ttrue\tfalse'),
            ('MATERIAL', '10\t11\tBASE\tFLAX\ttrue'),
            ('MATERIAL', '10\t12\tSPEC\tDYE\ttrue'),
            ('MATERIAL', '38\t39\tBASE\tWHEAT\tfalse')]}
        def host(q, city, plot, target, role, stage, **other):
            return relation(1,q,plot,target,11,'neighbourFirst',city=city,role=role,stage=stage,
                            **({'neighbourPillaged':'false'} | other))
        log = '\n'.join([host('TAILORS',7,10,20,'customer',2,building='A',buildingStatus=2),
            host('TAILORS',7,10,20,'sales',0), host('TAILORS',7,10,21,'goodsProvider',0),
            host('TAILORS',7,10,22,'customer',3,building='B'),
            record('RELATION_REMOVED',turn=14,relation='10:22:customer:3:B'),
            host('TAILORS',7,10,23,'customer',3,neighbourPillaged='true'),
            host('BAKERS',8,38,40,'customer',3), host('BAKERS',8,38,41,'sales',0,neighbourDistrict=0)])
        counts = endpoint_pair_supply(census,parse(log,'CSC_PLANNING_'),{1})
        self.assertEqual(counts,{'TAILORS:customer:partnerFirst':dict(completed=2,mapped_buyer_district=2,
            with_working_base=1,with_working_base_and_spec=1,with_working_base_and_customer_building=1),
            'TAILORS:provider:partnerFirst':dict(completed=1,with_working_base=1,with_working_base_and_spec=1),
            'BAKERS:customer:partnerFirst':dict(completed=1,mapped_buyer_district=1)})
        timed = endpoint_pair_supply(census,parse(log,'CSC_PLANNING_'),{1},include_timing=True)
        self.assertEqual(timed['TAILORS:customer:partnerFirst']['second_foundation_turns'],
                         dict(known=2,unknown=0,mean=5,median=5,maximum=5))

    def test_common_survey_needs_the_original_partner_city_to_complete(self):
        offer=('CSC_AI_SPATIAL_BID turn=3 player=1 city=7 district=43 plot=10 rank=1 adjacency=2.000 '
               'customerCity1=8 customerPlot1=20 customerType1=6 customerCity2=-1')
        log='\n'.join(['CSC_DISTRICT_CATALOGUE\t43\tDISTRICT_CSC_TAILORS_QUARTER\ttrue',offer,offer,
            record('FOUNDATION',turn=4,player=1,city=8,district=6,plot=20,foundationDateKnown='true'),
            record('FOUNDATION',turn=9,player=1,city=7,district=43,plot=10,foundationDateKnown='true'),
            relation(1,'TAILORS',10,20,10,'neighbourFirst',city=7,neighbourCity=12),
            relation(1,'TAILORS',10,20,12,'neighbourFirst',city=7,neighbourCity=8)])
        counts=common_layout_conversion(log,parse(log,'CSC_PLANNING_'),{1},15)['TAILORS:partnerFirst']
        self.assertEqual(counts,dict(eligible_pairs=1,both_founded=1,total_turns_between_foundations=5,
                                    both_completed_adjacent=1,total_turns_to_completed_pair_from_first_foundation=8))

    def test_exact_layout_links_to_active_endpoint_supply_under_the_original_owner(self):
        bid=('CSC_AI_SPATIAL_BID turn=3 player=1 city=7 district=43 plot=10 rank=1 adjacency=2.000 '
             'customerCity1=8 customerPlot1=20 customerType1=6 customerCity2=-1')
        log='\n'.join(['CSC_DISTRICT_CATALOGUE\t43\tDISTRICT_CSC_TAILORS_QUARTER\ttrue',bid,
            record('FOUNDATION',turn=4,player=1,city=8,district=6,plot=20,foundationDateKnown='true'),
            record('FOUNDATION',turn=9,player=1,city=7,district=43,plot=10,foundationDateKnown='true'),
            relation(1,'TAILORS',10,20,12,'neighbourFirst',city=7,neighbourCity=8,
                     neighbourPillaged='false',building='BUYER',buildingStatus=2)])
        observed = parse(log, 'CSC_PLANNING_')
        census = {'turn':15, 'rows':[('QUARTER','TAILORS\t1\t7\t10\ttrue\tfalse'),
            ('MATERIAL','10\t11\tBASE\tFLAX\ttrue')]}
        def cohort():
            pairs=endpoint_pair_facts(census, observed, {1,2})
            counts,_=common_layout_report(log, observed, {1,2},15,endpoint_pairs=pairs)
            return counts['TAILORS:partnerFirst']
        self.assertEqual(cohort()['completed_with_working_base_at_endpoint'],1)
        self.assertEqual(cohort()['completed_with_working_base_and_buyer_at_endpoint'],1)
        census['rows'][0]=('QUARTER','TAILORS\t2\t9\t10\ttrue\tfalse')
        self.assertEqual(cohort()['both_completed_adjacent'],1)
        self.assertEqual(cohort()['completed_with_working_base_at_endpoint'],0)
        self.assertEqual(cohort()['completed_with_working_base_and_buyer_at_endpoint'],0)

    def test_actual_adjacent_partner_can_precede_the_surveyed_quarter(self):
        quarter = (1, 7, 43, 10)
        hub = (1, 8, 6, 20)
        targets = {('TAILORS', 'quarterFirst', quarter, hub[:3]): {21, 22},
                   ('TAILORS', 'partnerFirst', hub, quarter[:3]): {10, 11},
                   ('TAILORS', 'quarterFirst', quarter, (1, 9, 6)): {23},
                   ('TAILORS', 'quarterFirst', quarter, (1, 7, 5)): {24}}
        # The same completed pair fulfilled two surveyed targets. The actual
        # Hub was founded first. The other city's Hub qualified for neither.
        links = {(1,7,'TAILORS',10,8,6,20): 18}
        found = {quarter:15, hub:7, (1,9,6,25):21}
        result = anchored_target_results(targets, found, links, {'TAILORS':43})
        self.assertEqual(result['targets_by_first_surveyed_tile'], {
            'TAILORS:quarterFirst': {'completed_on_other_adjacent_tile':1,
                'second_type_founded_elsewhere_without_completed_link':1, 'second_type_never_founded_in_city':1},
            'TAILORS:partnerFirst': {'completed_on_surveyed_tiles':1}})
        self.assertEqual(result['distinct_completed_pairs_by_actual_order'], {'TAILORS':{'partnerFirst':1}})

    def test_purchased_customer_tile_joins_the_district_request_and_debit(self):
        log = '\n'.join(['CSC_CUSTOMER_LAND_WATCH_INSTALLED',
            'CSC_AI_CUSTOMER_LAND_OFFER turn=7 player=1 city=5 district=4 plot=23 invoice=40 bidQ8=200 version=3',
            'CSC_AI_CUSTOMER_RECEIPT turn=8 version=3 player=1 city=5 district=4 plot=23 result={"writes":1}',
            'CSC_AI_CUSTOMER_RECEIPT turn=8 version=3 player=1 city=5 district=4 plot=24 result={"writes":0}',
            'CSC_CUSTOMER_TREASURY\t8\t1\t7\t64.10\t24.10',
            'CSC_CUSTOMER_PLOT_PURCHASE\t8\t1\t8\t5\t23\t3\t2',
            record('FOUNDATION', turn=10, player=1, city=5, district=4, plot=23, foundationDateKnown='true')])
        rows = [[str(turn),'1','City TEST','Build City District','RUNNING','Purchase Plot',f'Purchase 3 2: {state} on #12']
                for turn,state in [(7,'Accepted'),(8,'Accepted'),(9,'Done')]]
        history = parse(log,'CSC_PLANNING_')
        result = customer_land_purchases(log,history,{1},15,rows)
        purchase, = result['purchases']
        offer, = result['offers']
        self.assertEqual((offer['version'], offer['delta_q8'], offer['receipt'], offer['logged_after_commit']),
                         (3, 200, {"writes":1}, True))
        self.assertEqual((purchase['district_request_turn'],purchase['matching_debit'],purchase['foundation']), (8,True,(10,4)))
        self.assertEqual(purchase['request_history'][-1], (9,12,'Done','City TEST'))
        partial = customer_land_purchases(log,history,{1},8,rows)
        self.assertEqual(partial['purchases'][0]['request_history'][-1][2], 'Accepted')
        self.assertEqual(partial['districts_on_purchased_plots'], [])
        ambiguous = log + '\nCSC_CUSTOMER_PLOT_PURCHASE\t8\t1\t6\t7\t25\t5\t2'
        self.assertFalse(customer_land_purchases(ambiguous,history,{1},15,rows)['purchases'][0]['matching_debit'])

    def test_organic_partner_land_can_complete_a_pair_without_a_planner_offer(self):
        log = '\n'.join(['CSC_CUSTOMER_LAND_WATCH_INSTALLED',
            'CSC_CUSTOMER_PLOT_PURCHASE\t7\t1\t8\t5\t23\t3\t2',
            record('FOUNDATION', turn=9, player=1, city=5, district=4, plot=23, foundationDateKnown='true'),
            *[relation(1,'TAILORS',10,23,11,'quarterFirst',neighbourCity=city,neighbourDistrict=4,role=role)
              for city,role in ((6,'customer'),(5,'customer'),(5,'sales'))]])
        result = customer_land_purchases(log,parse(log,'CSC_PLANNING_'),{1},15,[])
        self.assertEqual((result['offered_tiles'], result['purchases']), (0, []))
        self.assertEqual(result['ai_plot_purchases'], 1)
        acquisition, = result['observed_plot_purchases']
        self.assertEqual((acquisition['turn'], acquisition['plot'], acquisition['foundation']), (7,23,(9,4)))
        self.assertEqual(result['districts_on_purchased_plots'], [
            dict(player=1,city=5,plot=23,bought=7,founded=9,district=4)])
        self.assertEqual(result['completed_partners_on_purchased_land'], [
            dict(player=1,city=5,plot=23,quarter='TAILORS',quarter_plot=10,district=4,bought=7,founded=9,linked=11)])

    def test_short_replay_does_not_count_a_different_customer_on_the_same_tile(self):
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            for name in ('complete.json', 'session-closed.json'):
                (folder / name).write_text('{"verified":true}', encoding='utf-8')
            (folder / 'observed-services.json').write_text('{"chains":[]}', encoding='utf-8')
            (folder / 'Lua.log').write_text('\n'.join(
                'CSC_AI_PROSPECTIVE_CONNECTION turn=3 player=1 quarterCity=7 quarter=43 quarterPlot=10 '
                f'customerCity=8 customer={district} customerPlot=20' for district in (6, 7)), encoding='utf-8')
            rows = trace_arm(folder, ((7, 43, 10), (8, 6, 20)), 1, {})
        self.assertEqual([row['customer'] for row in rows['proposals']], [6])
        self.assertEqual([row['customer'] for row in rows['related_proposals']], [7])

    def test_short_replay_joins_a_completed_purchase_to_its_own_city(self):
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            for name in ('complete.json', 'session-closed.json'):
                (folder / name).write_text('{"verified":true,"turn":15}', encoding='utf-8')
            (folder / 'observed-services.json').write_text('{"chains":[]}', encoding='utf-8')
            def winner(version):
                row = dict(player=1, city=5, district=4, plot=23, k='best', eligible=1, reservationId=-1,
                           version=version, generation=version, result=200)
                return f'CSC_CUSTOMER_WATCH_NATIVE observedTurn=9 generation={version} ordinal=4 record=' + json.dumps(row)

            def provider_mask(version):
                row=dict(player=1, city=5, district=5, plot=23, k='decline', eligible=1,
                         version=version, generation=version, base=250, result=-262145)
                return f'CSC_CUSTOMER_WATCH_NATIVE observedTurn=9 generation={version} ordinal=3 record=' + json.dumps(row)

            replay_log = '\n'.join([
                'CSC_CUSTOMER_LAND_WATCH_INSTALLED',
                record('PUBLICATION',turn=7,version=3,pendingTurn=7,accepted='true'),
                record('PUBLICATION',turn=8,version=4,pendingTurn=8,accepted='true'),
                'CSC_AI_CUSTOMER_LAND_APPRAISED turn=8 player=1 city=5 district=4 plot=23 invoice=40 ownedMarginQ8=800 scarcityQ8=-100 creditQ8=200 slotWait=4',
                'CSC_AI_CUSTOMER_LAND_APPRAISED turn=8 player=1 city=5 district=5 plot=23 invoice=40 ownedMarginQ8=800 scarcityQ8=-100 creditQ8=200',
                'CSC_AI_CUSTOMER_LAND_OFFER turn=7 player=1 city=5 district=4 plot=23 invoice=40',
                'CSC_CUSTOMER_TREASURY\t10\t1\t7\t100.50\t60.50',
                'CSC_CUSTOMER_PLOT_PURCHASE\t10\t1\t8\t5\t23\t3\t2',
                'CSC_AI_PROVIDER_DECLINE_PROPOSED turn=8 version=4 player=1 city=5 district=5 alternative=4 alternativePlot=23 sites=2',
                'CSC_AI_PROVIDER_DECLINE_PROPOSED turn=8 version=5 player=1 city=5 district=5 alternative=4 alternativePlot=23 sites=2',
                provider_mask(4),
                provider_mask(5),
                winner(3),
                winner(4),
                record('FOUNDATION', turn=10, player=1, city=5, district=4, plot=23, foundationDateKnown='true'),
                relation(1,'TAILORS',10,23,11,'quarterFirst',city=7,neighbourCity=6,neighbourDistrict=4),
                relation(1,'TAILORS',10,23,12,'quarterFirst',city=7,neighbourCity=5,neighbourDistrict=4),
                record('MATERIAL_STATE',turn=13,player=1,quarter='TAILORS',quarterPlot=10,materialPlot=9,
                       owner=1,working='true',base='true',spec='false'),
            ])
            (folder / 'Lua.log').write_text(replay_log, encoding='utf-8')
            with (folder/'AI_Behavior_Trees.csv').open('w', encoding='utf-8') as out:
                out.write('7,1,City BUYER,Build City District,RUNNING,Purchase Plot,Purchase 3 2: Accepted on #12\n')
                out.write('8,1,City OTHER,Build City District,RUNNING,Purchase Plot,Purchase 3 2: Accepted on #13\n')
            (folder/'AI_CityBuild.csv').touch()
            def trace():
                return trace_arm(folder, ((7,43,10),(5,4,23)), 1,
                                 {43:'DISTRICT_CSC_TAILORS_QUARTER',4:'DISTRICT_HARBOR'}, 10,
                                 {5:'BUYER'}, switch_turn=7)

            rows = trace()
            (folder / 'Lua.log').write_text(replay_log.replace(
                'turn=7 player=1 city=5 district=4 plot=23 invoice=40',
                'turn=8 player=1 city=5 district=4 plot=23 invoice=40 bidQ8=200 version=4'
            ) + '\nCSC_AI_CUSTOMER_RECEIPT turn=9 version=4 player=1 city=5 district=4 plot=23 result={"writes":1}',
                encoding='utf-8')
            trigger = '9,1,City BUYER,Build City District,SUCCESS,Decode Trigger,District: DISTRICT_HARBOR; Value: 200\n'
            request = trigger + '9,1,City BUYER,Build City District,RUNNING,Purchase Plot,Purchase 3 2: Accepted on #12\n'
            path = folder / 'AI_Behavior_Trees.csv'
            path.write_text(request, encoding='utf-8')
            fresh, = trace()['exact_customer_land']['spending']
            choice, = fresh['switched_native_choices_at_first_acceptance']
            self.assertEqual((fresh['first_observed_buying_city_acceptance'], choice['version'], choice['invoice']), (9,4,40))
            self.assertEqual(fresh['first_observed_request_district'], 'DISTRICT_HARBOR')
            proof_log = (folder/'Lua.log').read_text(encoding='utf-8')
            (folder/'Lua.log').write_text(proof_log.replace('CSC_CUSTOMER_TREASURY',
                'CSC_AI_CUSTOMER_LAND_OFFER turn=9 player=1 city=5 district=7 plot=23 invoice=60 bidQ8=100 version=5\n'
                'CSC_CUSTOMER_TREASURY'), encoding='utf-8')
            qualified, = trace()['exact_customer_land']['spending']
            self.assertEqual(qualified['quotes'], [(7,60)])
            self.assertEqual([c['version'] for c in qualified['switched_native_choices_at_first_acceptance']], [4])
            (folder/'Lua.log').write_text(proof_log, encoding='utf-8')
            path.write_text(request.replace('DISTRICT_HARBOR', 'DISTRICT_MBANZA'), encoding='utf-8')
            competing, = trace()['exact_customer_land']['spending']
            self.assertEqual(competing['first_observed_request_district'], 'DISTRICT_MBANZA')
            self.assertEqual(competing['switched_native_choices_at_first_acceptance'], [])
            path.write_text(request.replace('9,1,','4,1,').replace('Accepted', 'Submitted') + request, encoding='utf-8')
            retained, = trace()['exact_customer_land']['spending']
            self.assertEqual((retained['first_observed_buying_city_request'],
                              retained['first_observed_buying_city_acceptance']), (4,9))
            self.assertEqual(retained['switched_native_choices_at_first_acceptance'], [])
            unrelated_city = trigger.replace('City BUYER', 'City OTHER')
            path.write_text(request.replace(trigger, unrelated_city), encoding='utf-8')
            unknown, = trace()['exact_customer_land']['spending']
            self.assertIsNone(unknown['first_observed_request_district'])
            self.assertEqual(unknown['switched_native_choices_at_first_acceptance'], [])
        self.assertEqual(rows['exact_pair_build_order'], 'quarterFirst')
        self.assertEqual(rows['exact_pair_first_completed_link']['turn'], 12)
        self.assertTrue(rows['exact_pair_first_completed_after_switch'])
        self.assertEqual([row['post_switch_packet'] for row in rows['comparisons']], [False, True])
        self.assertEqual([p['publication_accepted'] for p in rows['provider_admission_proposals']], [True, False])
        mask,=rows['provider_admission_masks']
        self.assertEqual((mask['district'],mask['plot'],mask['masked_q8']), (5,23,-262145))
        self.assertEqual(mask['generation'],rows['comparisons'][-1]['generation'])
        self.assertLess(mask['ordinal'],rows['comparisons'][-1]['ordinal'])
        self.assertEqual(rows['quarter_materials']['working_at_endpoint'], {'TAILORS:BASE':1})
        purchase, = rows['exact_customer_land']['spending']
        self.assertTrue(purchase['matching_debit'] and purchase['built_offered_type'])
        self.assertFalse(purchase['offer_during_post_switch_publication'])
        self.assertTrue(purchase['purchase_after_switch'])
        self.assertEqual((purchase['district_request_turn'], purchase['buying_city_request_turn']), (8,7))
        appraisal, = rows['exact_customer_land']['appraisals']
        self.assertEqual((appraisal['owned_margin_q8'], appraisal['scarcity_q8'], appraisal['credit_q8'],
                          appraisal['slot_wait'], appraisal['post_switch']), (800,-100,200,4,True))
        acquisition, = rows['exact_customer_land']['acquisitions']
        self.assertEqual(acquisition['treasury_changes'], [40.0])
        linked, = rows['exact_customer_land']['completed_on_purchased_plot']
        self.assertEqual(linked['linked'], 12)

    def test_failed_bids_use_scores_seen_before_the_exact_native_winner(self):
        def n(kind, ordinal, plot, base, result):
            return ('CSC_CUSTOMER_WATCH_NATIVE observedTurn=5 generation=6 '
                    f'ordinal={ordinal} record={{"k":"{kind}","generation":6,"version":4,"player":1,'
                    f'"city":7,"district":6,"plot":{plot},"base":{base},"result":{result},"eligible":1}}')

        log = '\n'.join([
            'CSC_DISTRICT_CATALOGUE\t33\tDISTRICT_RURALCOMMUNITYA\ttrue',
            record('PUBLICATION', accepted='true', version=4, pendingTurn=4),
            record('OPPORTUNITY', turn=4, version=4, player=1, city=7, district=43, plot=10, offered='true', bidQ8=120),
            record('OPPORTUNITY', turn=4, version=4, player=1, city=7, district=43, plot=12, offered='true', bidQ8=200),
            'CSC_AI_CUSTOMER_FUTURE_BID turn=4 player=1 city=7 district=6 plot=20 deltaQ8=16',
            'CSC_QUARTER_WATCH_WRITE\tversion=4\tplayer=1\tcity=7\tdistrict=43\tplot=10\tresult=120\t'
            'eligible=1\tgeneration=6\tnativeOrdinal=13',
            'CSC_QUARTER_WATCH_WRITE\tversion=4\tplayer=1\tcity=7\tdistrict=43\tplot=12\tresult=200\t'
            'eligible=1\tgeneration=6\tnativeOrdinal=35',
            n('net', 14, 20, 54, 70), n('cache', 16, 20, 91, 91),
            record('NATIVE_BEST', turn=5, version=4, player=1, city=7, district=33, plot=15,
                   nativeOrdinal=20, generation=6, result=160),
        ])
        competition = bid_competition(log, parse(log, 'CSC_PLANNING_'), {1}, 250)
        self.assertEqual(competition['lost_to'], {kind: {'DISTRICT_RURALCOMMUNITYA': 1}
                                                 for kind in ('quarter', 'customer')})
        self.assertEqual({loss['kind']: loss['gap_q8'] for loss in competition['losses']},
                         {'quarter': 40, 'customer': 69})
        reference = log.replace('CSC_AI_CUSTOMER_FUTURE_BID', 'CSC_AI_CONNECTION_COMPLETION').replace(
            'deltaQ8=16', 'order=quarterFirst creditQ8=16')
        self.assertEqual(bid_competition(reference,parse(reference,'CSC_PLANNING_'),{1},250),competition)
        quarter_credit = reference.replace('order=quarterFirst','order=customerFirst')
        self.assertNotIn('customer',bid_competition(quarter_credit,parse(quarter_credit,'CSC_PLANNING_'),{1},250)['lost_to'])

    def test_expired_request_lists_actual_production_in_the_right_owner_window(self):
        district = 'DISTRICT_CSC_TAILORS_QUARTER'
        submit = ['4', '1', 'CITY_A', '', 'CONTRACT 11', 'SUBMITTED', 'NO_UNIT', 'NO_BUILDING', district]
        failed = ['6', '1', 'CITY_A', '', 'CONTRACT 11', 'FAILED', 'NO_UNIT', 'NO_BUILDING', district]
        result = failed_district_requests([submit, ['5', '1', 'CITY_A'], failed, ['6', '2', 'CITY_A']],
            [['4', 'CITY_A', '2.0', 'UNIT_BUILDER'], ['5', 'CITY_A', '10.0', 'UNIT_BUILDER'],
             ['6', 'CITY_A', '1.0', 'UNIT_ARCHER']], {1}, {district}, 250)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['contract'], 'CONTRACT 11')
        self.assertEqual(result[0]['concurrent_production_turns'], {'UNIT_BUILDER': 2})

    def test_footprint_loss_uses_the_cell_at_risk_instead_of_the_best_other_site(self):
        log = '\n'.join([
            'CSC_DISTRICT_CATALOGUE\t33\tDISTRICT_RURALCOMMUNITYA\tfalse',
            'CSC_DISTRICT_CATALOGUE\t43\tDISTRICT_CSC_TAILORS_QUARTER\ttrue',
            record('OPPORTUNITY', turn=4, version=4, player=1, city=7, district=43,
                   plot=10, offered='true', bidQ8=120),
            record('OPPORTUNITY', turn=4, version=4, player=1, city=7, district=43,
                   plot=12, offered='true', bidQ8=150),
            'CSC_QUARTER_WATCH_WRITE\tversion=4\tplayer=1\tcity=7\tdistrict=43\tplot=10\tresult=120\t'
            'eligible=1\tgeneration=6\tnativeOrdinal=13',
            'CSC_QUARTER_WATCH_WRITE\tversion=4\tplayer=1\tcity=7\tdistrict=43\tplot=12\tresult=150\t'
            'eligible=1\tgeneration=6\tnativeOrdinal=14',
            record('NATIVE_BEST', turn=5, version=4, player=1, city=7, district=33, plot=10,
                   nativeOrdinal=20, generation=6, result=160),
        ])
        results = bid_competition(log, parse(log, 'CSC_PLANNING_'), {1}, 250)
        strongest, = results['losses']
        contested, = results['footprint_losses']
        self.assertEqual((strongest['plot'], strongest['gap_q8']), (12, 10))
        self.assertEqual((contested['plot'], contested['gap_q8']), (10, 40))

        tied = log.removesuffix('160') + '120'
        results = bid_competition(tied, parse(tied, 'CSC_PLANNING_'), {1}, 250)
        self.assertEqual(results['losses'], [])
        self.assertEqual([loss['gap_q8'] for loss in results['footprint_losses']], [0])

    def test_prospective_layout_follows_exact_packet_and_both_foundations(self):
        def plan(target):
            return ('CSC_AI_STRONG_QUARTER_LAYOUT turn=3 player=1 city=7 district=43 plot=10 '
                    f'customerCity=8 customerDistrict=6 customerPlot={target} stage=3 '
                    'existing=false extraBase=true specialty=false')

        log = '\n'.join([
            'CSC_DISTRICT_CATALOGUE\t43\tDISTRICT_CSC_TAILORS_QUARTER\ttrue',
            plan(20), plan(22), plan(20),
            record('OPPORTUNITY', player=1, city=7, district=43, plot=10,
                   turn=3, version=2, offered='true', bidQ8=120),
            'CSC_QUARTER_WATCH_WRITE\tplayer=1\tcity=7\tdistrict=43\tplot=10\tversion=2\teligible=1\tresult=120',
            'CSC_QUARTER_WATCH_BEST\tplayer=1\tcity=7\tdistrict=43\tplot=10\tversion=1\teligible=1\tresult=120',
            record('FOUNDATION', player=1, city=7, district=43, plot=10, turn=4, foundationDateKnown='true'),
            relation(1, 'TAILORS', 10, 20, 12, 'quarterFirst', city=7, neighbourCity=8, stage=3),
        ])
        groups = prospective_layouts(log, parse(log, 'CSC_PLANNING_'), {1}, 250)
        self.assertEqual(groups, {'TAILORS:TWO_BASE': dict(layouts=2, published=2, native_score_write=2,
                                                          native_best=0, quarter_founded=2, completed_pair=1)})

    def test_priced_pair_can_complete_on_one_named_substitute(self):
        log = '\n'.join([
            'CSC_DISTRICT_CATALOGUE\t43\tDISTRICT_CSC_TAILORS_QUARTER\ttrue',
            'CSC_DISTRICT_CATALOGUE\t4\tDISTRICT_HARBOR\ttrue',
            'CSC_AI_PROSPECTIVE_CONNECTION turn=5 player=1 quarterCity=7 quarter=43 quarterPlot=10 '
            'customerCity=8 customer=4 customerPlot=20 valueQ8=512',
            'CSC_AI_PROSPECTIVE_SUBSTITUTE turn=5 player=1 quarterCity=7 quarter=43 quarterPlot=10 '
            'customerCity=8 customer=4 customerPlot=20 alternateQuarterPlot=11 alternateCustomerPlot=21',
            record('MAPPING',district=4,districtType='DISTRICT_HARBOR'),
            *[relation(1,'TAILORS',q,p,12,'quarterFirst',city=7,neighbourCity=city,neighbourDistrict=4,
                       quarterFoundationTurn=qt,neighbourFoundationTurn=pt)
              for q,p,city,qt,pt in ((11,21,8,5,6),(10,21,9,5,6),(11,20,8,6,3),(10,21,8,5,7),(10,21,8,5,7))]])
        observations = parse(log,'CSC_PLANNING_')
        rows = prospective_footprints(log,observations,{1},15,{'footprint_losses':[]},priced=True)
        self.assertEqual(len(rows),1)
        result, = completed_substitute_pairs(rows,observations,15)
        self.assertEqual((result['quarter_plot'],result['partner_plot'],result['alternate_seen']), (10,21,5))
        self.assertEqual((result['partner_founded'],result['both_complete_by']), (7,12))

    def test_prospective_footprints_separate_native_choices_from_later_occupation(self):
        log = '\n'.join([
            'CSC_DISTRICT_CATALOGUE\t43\tDISTRICT_CSC_TAILORS_QUARTER\ttrue',
            'CSC_DISTRICT_CATALOGUE\t6\tDISTRICT_HARBOR\ttrue',
            'CSC_DISTRICT_CATALOGUE\t33\tDISTRICT_RURALCOMMUNITYA\tfalse',
            'CSC_AI_STRONG_QUARTER_LAYOUT turn=3 player=1 city=7 district=43 plot=10 '
            'customerCity=8 customerDistrict=6 customerPlot=20 stage=2 existing=false extraBase=true specialty=false',
            'CSC_AI_PROSPECTIVE_SUBSTITUTE turn=3 player=1 quarterCity=7 quarter=43 quarterPlot=10 '
            'customerCity=8 customer=6 customerPlot=20 alternateQuarterPlot=-1 alternateCustomerPlot=21',
            record('PUBLICATION', accepted='true', pendingTurn=3, version=2),
            record('NATIVE_BEST', turn=4, version=2, player=1, city=7, district=33, plot=10),
            record('NATIVE_BEST', turn=5, version=3, player=1, city=8, district=6, plot=20),
            record('NATIVE_BEST', turn=4, version=2, player=1, city=8, district=33, plot=20,
                   generation=6, nativeOrdinal=20, result=60),
            'CSC_CUSTOMER_WATCH_NATIVE observedTurn=4 generation=6 ordinal=12 record={"k":"cache",'
            '"generation":6,"version":2,"player":1,"city":8,"district":6,"plot":20,"result":47,"eligible":1}',
            'CSC_CUSTOMER_WATCH_NATIVE observedTurn=4 generation=6 ordinal=30 record={"k":"cache",'
            '"generation":6,"version":2,"player":1,"city":8,"district":6,"plot":20,"result":59,"eligible":1}',
            record('FOUNDATION', turn=5, foundationTurn=5, foundationDateKnown='true',
                   player=1, city=7, district=43, plot=10),
            record('NATIVE_BEST', turn=8, version=7, player=1, city=8, district=6, plot=23,
                   generation=9, nativeOrdinal=15, result=42),
            'CSC_CUSTOMER_WATCH_NATIVE observedTurn=8 generation=9 ordinal=15 record={"k":"best",'
            '"generation":9,"version":7,"player":1,"city":8,"district":6,"plot":23,"result":42,"eligible":1}',
            record('NATIVE_BEST', turn=11, version=10, player=1, city=8, district=6, plot=24,
                   generation=10, nativeOrdinal=16, result=50),
            record('FOUNDATION', turn=10, foundationTurn=10, foundationDateKnown='true',
                   player=2, city=9, district=33, plot=20),
        ])
        loss = dict(version=2, player=1, city=7, district='DISTRICT_CSC_TAILORS_QUARTER', plot=10,
                    winner_plot=10, gap_q8=7)
        row, = prospective_footprints(log, parse(log, 'CSC_PLANNING_'), {1}, 25, {'footprint_losses': [loss]})
        self.assertEqual(row['quarter']['native_same_plot_choices'], {'DISTRICT_RURALCOMMUNITYA': 1})
        self.assertEqual(row['quarter']['nearest_loss'], loss)
        self.assertEqual(row['observed_substitutes'], [dict(turn=3, versions=[2], quarter_plot=-1, customer_plot=21)])
        self.assertTrue(row['quarter']['first_occupation']['matched'])
        self.assertEqual(row['customer']['native_same_plot_choices'], {'DISTRICT_RURALCOMMUNITYA': 1})
        self.assertEqual(row['customer']['exact_same_plot_losses'], 0)
        self.assertEqual(row['customer']['nearest_cached_loss']['gap_q8'], 13)
        self.assertFalse(row['customer']['first_occupation']['matched'])
        self.assertEqual(row['customer']['first_occupation']['player'], 2)
        self.assertEqual(row['post_foundation_choices'], {'customer': dict(observed_choices=1,
                         exact_target=0, same_type_elsewhere=[dict(observed_turn=8,plot=23)], other_districts={})})

    def test_strong_pair_counts_each_physical_customer_once_across_stages(self):
        offer = ('CSC_AI_STRONG_QUARTER_LAYOUT turn=3 player=1 city=7 district=43 plot=10 '
                 'customerCity=8 customerDistrict=6 customerPlot=20 stage={} '
                 'existing=false extraBase=true specialty=false')
        log = '\n'.join([
            'CSC_DISTRICT_CATALOGUE\t43\tDISTRICT_CSC_TAILORS_QUARTER\ttrue',
            'CSC_DISTRICT_CATALOGUE\t6\tDISTRICT_HARBOR\ttrue',
            offer.format(2), offer.format(3),
            record('PUBLICATION', accepted='true', pendingTurn=3, version=2),
            record('OPPORTUNITY', turn=3, version=2, player=1, city=7, district=43, plot=10, offered='true'),
            record('FOUNDATION', turn=5, foundationDateKnown='true', player=1, city=8, district=6, plot=20),
            record('FOUNDATION', turn=6, foundationDateKnown='true', player=1, city=7, district=43, plot=10),
            record('COMPLETION', turn=7, player=1, city=7, district=43, plot=10),
            record('COMPLETION', turn=8, player=1, city=8, district=6, plot=20),
        ])
        rows = prospective_footprints(log, parse(log, 'CSC_PLANNING_'), {1}, 25, {'footprint_losses': []})
        counts = prospective_footprint_counts(rows)['DISTRICT_CSC_TAILORS_QUARTER']
        self.assertEqual((counts['modeled_pairs'], counts['pairs_with_quarter_offer'],
                          counts['pairs_completed'], counts['completed_customer_first']), (1, 1, 1, 1))
        self.assertEqual(counts['turns_between_foundations_customer_first'], 1)
        self.assertEqual(counts['turns_from_first_foundation_to_both_complete_customer_first'], 3)

    def test_single_base_provider_pair_keeps_its_role_and_build_order(self):
        log = '\n'.join([
            'CSC_DISTRICT_CATALOGUE\t43\tDISTRICT_CSC_TAILORS_QUARTER\ttrue',
            'CSC_AI_STRONG_QUARTER_LAYOUT turn=3 player=1 city=7 district=43 plot=10 '
            'customerCity=8 customerDistrict=6 customerPlot=20 stage=0 existing=false extraBase=false specialty=false',
            'CSC_AI_CONNECTION_OPPORTUNITY turn=5 player=1 identity=customerFirst:20:0:TAILORS:7:43:10',
            relation(1,'TAILORS',10,20,12,'neighbourFirst',role='goodsProvider',city=7,neighbourCity=8),
        ])
        observations = parse(log, 'CSC_PLANNING_')
        self.assertEqual(prospective_layouts(log, observations, {1}, 25)['TAILORS:ONE_BASE']['completed_pair'], 1)
        counts = connection_counts(log, {1}, 25, observations=observations)
        self.assertEqual(counts['completed_provider_pairs'], {'providerFirst:TAILORS': 1})
        self.assertEqual(counts['provider_district_opportunities'], {'customerFirst:TAILORS': 1})
        self.assertEqual(counts['completed_provider_opportunities'], {'customerFirst:TAILORS': 1})
        self.assertEqual(counts['completed_physical_pairs'], {})

    def test_folds_stage_duplicates_and_joins_both_orders(self):
        log = '\n'.join([
            'CSC_AI_CONNECTION_OPPORTUNITY turn=5 player=1 identity=quarterFirst:10:3:BAKERS:7:6:20',
            'CSC_AI_CONNECTION_OPPORTUNITY turn=6 player=1 identity=quarterFirst:10:4:BAKERS:7:6:20',
            'CSC_AI_CONNECTION_OPPORTUNITY turn=5 player=2 identity=customerFirst:30:3:TAILORS:8:43:40',
            relation(1, 'BAKERS', 10, 20, 9, 'quarterFirst', neighbourComplete='false'),
            relation(1, 'BAKERS', 10, 20, 12, 'quarterFirst'),
            relation(2, 'TAILORS', 40, 30, 13, 'neighbourFirst'),
            relation(2, 'BAKERS', 10, 20, 15, 'quarterFirst'),  # same physical pair after capture
        ])
        counts = connection_counts(log, {1, 2}, 20)
        expected = {'quarterFirst:BAKERS': 1, 'customerFirst:TAILORS': 1}
        self.assertEqual(counts['opportunities'], expected)
        self.assertEqual(counts['completed_opportunities'], expected)
        self.assertEqual(counts['district_opportunities'], expected)
        self.assertEqual(counts['completed_district_opportunities'], expected)
        self.assertEqual(counts['completed_physical_pairs'], expected)

    def test_unrelated_foundation_takes_footprint_and_capture_cannot_convert(self):
        log = '\n'.join([
            'CSC_AI_CONNECTION_OPPORTUNITY turn=5 player=1 identity=quarterFirst:10:3:BAKERS:7:6:20',
            'CSC_AI_CONNECTION_OPPORTUNITY turn=5 player=1 identity=quarterFirst:10:3:BAKERS:7:6:21',
            record('FOUNDATION', player=1, plot=20, district=8, turn=9, foundationDateKnown='true'),
            relation(2, 'BAKERS', 10, 21, 15, 'quarterFirst'),
            relation(1, 'BAKERS', 10, 20, 16, 'quarterFirst', neighbourDistrict=8),
        ])
        counts = connection_counts(log, {1, 2}, 20)
        self.assertEqual(counts['opportunities'], {'quarterFirst:BAKERS': 2})
        self.assertEqual(counts['district_opportunities'], {'quarterFirst:BAKERS': 1})
        self.assertEqual(counts['completed_opportunities'], {})
        self.assertEqual(counts['lost_to_other_foundations'], {'quarterFirst:BAKERS': 1})

    def test_keeper_repair_and_ownership_change_count_separately(self):
        def material(plot, turn, *, working=True, player=1):
            return dict(kind='MATERIAL_STATE', player=player, owner=player, quarter='BAKERS',
                        quarterPlot=20, materialPlot=plot, base=True, spec=False, working=working, turn=turn)

        history = supplier_history([material(21, 3), material(22, 3), material(23, 3),
                                    material(22, 5, working=False), material(23, 6, player=0),
                                    material(22, 9)], {1}, 20)
        self.assertEqual(history, dict(ever_working={'BAKERS:BASE': 3}, working_at_endpoint={'BAKERS:BASE': 2},
                                       working_without_observed_loss={'BAKERS:BASE': 1},
                                       working_again_after_loss={'BAKERS:BASE': 1}))

    def test_foreign_and_reassigned_foundations_close_owned_opportunities(self):
        log = '\n'.join([
            'CSC_AI_CONNECTION_OPPORTUNITY turn=5 player=1 identity=quarterFirst:10:3:BAKERS:7:6:20',
            'CSC_AI_CONNECTION_OPPORTUNITY turn=5 player=1 identity=quarterFirst:10:3:BAKERS:7:6:21',
            record('FOUNDATION', player=0, city=8, plot=20, district=6, turn=9, foundationDateKnown='true'),
            record('FOUNDATION', player=1, city=9, plot=21, district=6, turn=9, foundationDateKnown='true'),
        ])
        counts = connection_counts(log, {1}, 20)
        self.assertEqual(counts['lost_to_other_foundations'], {'quarterFirst:BAKERS': 2})
        self.assertEqual(counts['lost_to_foreign_foundations'], {'quarterFirst:BAKERS': 1})

    def test_wonder_foundation_is_distinct_from_exact_completed_building(self):
        log = '\n'.join([
            'CSC_AI_WONDER_CONNECTION_OPPORTUNITY turn=5 player=1 order=quarterFirst quarter=TAILORS '
            'anchor=10 building=BUILDING_BROADWAY city=7 plot=20',
            'CSC_AI_WONDER_CONNECTION_OPPORTUNITY turn=5 player=2 order=customerFirst quarter=TAILORS '
            'anchor=40 building=BUILDING_SYDNEY_OPERA_HOUSE city=8 plot=30',
            relation(1, 'TAILORS', 10, 20, 9, 'quarterFirst', role='wonderCustomer',
                     neighbourDistrict=13, building='BUILDING_BROADWAY', buildingStatus=0),
            relation(1, 'TAILORS', 10, 20, 12, 'quarterFirst', role='wonderCustomer',
                     neighbourDistrict=13, building='BUILDING_BROADWAY', buildingStatus=2),
            relation(2, 'TAILORS', 30, 40, 12, 'neighbourFirst', role='wonderCustomer',
                     neighbourDistrict=13, building='BUILDING_SYDNEY_OPERA_HOUSE', buildingStatus=0),
        ])
        result = wonder_connections(log, parse(log, 'CSC_PLANNING_'), {1, 2}, 20)
        broadway = {'quarterFirst:TAILORS:BUILDING_BROADWAY': 1}
        self.assertEqual(sum(result['opportunities'].values()), 2)
        self.assertEqual(result['completed_opportunities'], broadway)
        self.assertEqual(result['completed_physical_pairs'], broadway)
