import unittest

from anchored_connection_results import connection_counts, supplier_history, wonder_connections
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
