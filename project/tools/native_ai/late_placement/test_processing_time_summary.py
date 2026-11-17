"""Timing aggregation uses actual attempts/turns and preserves missing data."""
import unittest
from processing_time_summary import summarise


class ProcessingTimes(unittest.TestCase):
    def test_retry_work_is_summed_and_native_packet_counter_is_not_duplicated(self):
        result=summarise('''
Lua: CSC_AI_PROCESSING turn=1 published=0 ok=0 wallMicros=1000 luaClockMicros=500
Lua: CSC_AI_PROCESSING turn=1 published=1 ok=1 wallMicros=3000 luaClockMicros=2000
Lua: CSC_AI_PROCESSING turn=2 published=1 ok=1 wallMicros=2000 luaClockMicros=1000
Lua: CSC_AI_PLAYER_PROCESSING turn=1 player=2 wallMicros=1500 luaClockMicros=1000 entries=3
Lua: CSC_AI_PLAYER_PROCESSING turn=2 player=2 wallMicros=1000 luaClockMicros=900 entries=2
Lua: CSC_AI_NATIVE_PROCESSING turn=1 version=4 managedMicros=100
Lua: CSC_AI_NATIVE_PROCESSING turn=1 version=4 managedMicros=150
''')
        self.assertEqual(result['publisher_wall']['average_ms'],3)
        self.assertEqual(result['publisher_wall']['max_ms'],4)
        self.assertEqual(result['publisher_wall']['slowest'][0],{'turn':1,'ms':4})
        self.assertEqual(result['publication_attempts'],3)
        self.assertEqual(result['failed_attempts'],1)
        self.assertEqual(result['native_managed_cell_wall']['total_ms'],.15)
        self.assertEqual(result['players']['2']['wall']['average_ms'],1.25)

    def test_missing_clock_is_reported_as_missing_and_startup_is_separate(self):
        result=summarise('''
CSC_AI_PROCESSING turn=0 published=1 ok=1 wallMicros=999999 luaClockMicros=88888
CSC_AI_PROCESSING turn=1 published=1 ok=1 wallMicros=-1 luaClockMicros=200
''')
        self.assertEqual(result['missing_wall_attempts'],1)
        self.assertEqual(result['publisher_wall']['turns'],0)
        self.assertIsNone(result['publisher_wall']['average_ms'])
        self.assertEqual(result['publisher_lua_clock']['average_ms'],.2)

    def test_a_missing_retry_never_makes_a_partial_turn_look_fast(self):
        result=summarise('''
CSC_AI_PROCESSING turn=1 published=0 ok=0 wallMicros=-1 luaClockMicros=200
CSC_AI_PROCESSING turn=1 published=1 ok=1 wallMicros=1000 luaClockMicros=500
CSC_AI_PROCESSING turn=3 published=1 ok=1 wallMicros=7000 luaClockMicros=2000
''',first=1,last=3)
        self.assertEqual(result['publisher_wall']['average_ms'],7)
        self.assertEqual(result['incomplete_wall_turns'],[1])
        self.assertEqual(result['unobserved_turns'],[2])


if __name__=='__main__':unittest.main()
