"""Guard against attributing later writes or equal nearby values to a decision."""
import unittest
from district_followthrough_results import fields, join_decisions


class DecisionJoin(unittest.TestCase):
    def test_last_numeric_field_does_not_absorb_line_ending(self):
        self.assertEqual(fields('phase=2\tversion=150\n'), dict(phase=2, version=150))

    def test_actual_call_clock_and_prior_same_generation_write(self):
        best = [dict(district=33, plot=1162, result=600000, generation=302,
                     nativeOrdinal=80, observedTurn=151, version=150)]
        calls = [dict(district=33, plot=1162, totalQ8=600000, turn=150)]
        writes = [dict(result=100, generation=300, nativeOrdinal=1),
                  dict(result=175006, generation=302, nativeOrdinal=70),
                  dict(result=900000, generation=302, nativeOrdinal=90)]
        row, = join_decisions(best, calls, writes)
        self.assertEqual((row['callTurn'], row['observedTurn']), (150, 151))
        self.assertEqual(row['candidateQ8'], 175006)
        row, = join_decisions(best, calls, writes[2:])
        self.assertFalse(row['exactFreshWrite'])
        self.assertIsNone(row['candidateQ8'])

    def test_changed_order_or_missing_stream_is_rejected(self):
        best = [dict(district=33, plot=1162, result=600000, generation=302,
                     nativeOrdinal=80, observedTurn=151, version=150)]
        with self.assertRaises(ValueError):
            join_decisions(best, [], [])
        with self.assertRaises(ValueError):
            join_decisions(best, [dict(district=33, plot=1163, totalQ8=600000, turn=150)], [])


if __name__ == '__main__':
    unittest.main()
