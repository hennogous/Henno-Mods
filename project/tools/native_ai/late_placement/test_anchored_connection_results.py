import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from anchored_connection_results import (bid_competition, connection_counts, failed_district_requests,
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
