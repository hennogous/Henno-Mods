"""Transport and settling failures must fail before native work is admitted."""
import json
import unittest

from driver import lua, parse, stable_sample, finish_contract
from full_game_controller.transport import NativeLuaFailure


class Contracts(unittest.TestCase):
    def test_known_repair_failure_remains_failed_while_other_probe_can_proceed(self):
        calls = []
        def finish():
            calls.append('validate')
            raise NativeLuaFailure('repair-quarter native Production delta city 1: actual 0, expected 1')
        def record():
            calls.append('record-only')
            return dict(validation='record-only')
        value = finish_contract('repair-quarter', finish, record)
        self.assertFalse(value['contract_passed'])
        self.assertEqual(value['validation'], 'record-only')
        self.assertEqual(calls, ['validate', 'record-only'])
        for case in ('wind-hill', 'water-6'):
            with self.assertRaises(NativeLuaFailure):
                finish_contract(case, finish, record)

    def test_lua_printable_ascii_roundtrip(self):
        from lupa.lua51 import LuaRuntime
        runtime = LuaRuntime(unpack_returned_tuples=True)
        for value in ('"\\', ''.join(map(chr, range(32, 127))), 'ABSENT'):
            self.assertEqual(runtime.eval(lua(value)), value)
        for value in ('a\x00', 'a\n', '\x7f', '水'):
            with self.assertRaises(ValueError):
                lua(value)

    def test_settling_is_not_a_wait_for_the_expected_answer(self):
        values = iter([dict(facts=[0]), dict(facts=[999]), dict(facts=[999])])
        self.assertEqual(stable_sample(lambda: next(values), clock=lambda: 0, pause=lambda _: None)['facts'], [999])

    def test_deadline_applies_after_a_slow_query(self):
        moment = [0]
        def query():
            moment[0] += 20
            return dict(facts=[1])
        with self.assertRaises(TimeoutError):
            stable_sample(query, clock=lambda: moment[0], timeout=30, pause=lambda _: None)

    def frames(self):
        payload = json.dumps(dict(text='é水' * 1000), ensure_ascii=False).encode()
        parts = [payload[i:i+512] for i in range(0, len(payload), 512)]
        return [dict(schema=1, part=i+1, parts=len(parts), bytes=len(payload),
            sum32=sum(payload) % 2**32, encoding='hex', data=v.hex()) for i, v in enumerate(parts)]

    def raw(self, frames):
        return '\n'.join('STATE: TEST_CHUNK=' + json.dumps(v) for v in frames)

    def test_chunked_unicode_receipt_is_lossless(self):
        frames = self.frames()
        self.assertEqual(parse(self.raw(frames), 'TEST')['text'], 'é水' * 1000)

    def test_missing_duplicate_reordered_and_corrupt_chunks_fail(self):
        frames = self.frames()
        bad = [dict(v) for v in frames]
        bad[0]['sum32'] += 1
        for sequence in (frames[:-1], frames + frames[:1], frames[1:] + frames[:1], bad):
            with self.assertRaises(ValueError):
                parse(self.raw(sequence), 'TEST')


if __name__ == '__main__':
    unittest.main()
