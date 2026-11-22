import unittest

from anchored_connection_results import connection_counts


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
