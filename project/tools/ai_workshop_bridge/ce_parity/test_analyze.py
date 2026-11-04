import unittest
import json
from pathlib import Path
import tempfile

from analyze import audit_records, marker_rows


def fixture():
    plans = {(5, 1): dict(entries=[
        dict(player=1, city=7, district=8, plot=30, delta=-65536),
        dict(player=1, city=7, district=9, plot=31, delta=1048576)])}
    def record(kind, **fields):
        return dict(k=kind, generation=5, version=1, player=1, city=7,
                    district=8, plot=30, base=5000, result=5000, reason=0,
                    eligible=1, **fields)
    negative = record('net')
    negative['result'] = -60536
    positive = record('net')
    positive.update(district=9, plot=31, result=1053576)
    return plans, {(5, 1, 0): negative, (5, 1, 1): positive,
                   (5, 1, 2): record('cache'), (5, 1, 3): record('best'),
                   (5, 1, 4): record('pv')}


class TraceAudit(unittest.TestCase):
    def test_both_signs_and_read_only_observers(self):
        value = audit_records(*fixture())
        self.assertEqual(value['adjustments'], dict(positive=1, negative=1))
        self.assertEqual(value['kinds'], dict(net=2, cache=1, best=1, pv=1))

    def test_exact_pair_and_human_exclusion(self):
        for field, value in (('plot', 32), ('player', 0)):
            plans, records = fixture()
            records[5, 1, 0][field] = value
            with self.assertRaises(ValueError):
                audit_records(plans, records)


class ChunkAudit(unittest.TestCase):
    def frames(self):
        value = dict(reason='published', status=dict(long='é水\n' * 700))
        raw = json.dumps(value, ensure_ascii=False).encode('utf-8')
        chunks = [raw[i:i + 512] for i in range(0, len(raw), 512)]
        frames = []
        for index, data in enumerate(chunks, 1):
            frame = dict(schema=1, epoch='g2-t1', seq=3, kind='NATIVE',
                part=index, parts=len(chunks), bytes=len(raw), sum32=sum(raw) % 2**32,
                encoding='hex', data=data.hex())
            frames.append('CSC_CE_Policy: CSC_CE_POLICY_CHUNK=' + json.dumps(frame) + '\n')
        return value, frames

    def read(self, frames):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'Lua.log'
            path.write_text(''.join(frames), encoding='utf-8')
            return list(marker_rows(path))

    def test_multibyte_long_receipt_reassembles(self):
        value, frames = self.frames()
        self.assertTrue(all(len(line.encode()) < 2047 for line in frames))
        actual = self.read(frames)
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0][1], value)

    def test_missing_duplicate_and_out_of_order_chunks_rejected(self):
        _, frames = self.frames()
        for damaged in (frames[:-1], frames[:1] + frames, frames[1:] + frames[:1]):
            with self.assertRaises(ValueError):
                self.read(damaged)

    def test_corrupt_payload_rejected(self):
        _, frames = self.frames()
        frames[-1] = frames[-1].replace('5c6e', '5c6f', 1)
        with self.assertRaises(ValueError):
            self.read(frames)

    def test_signed_floor(self):
        plans, records = fixture()
        records[5, 1, 0].update(base=-1048500, result=-1048576)
        self.assertEqual(audit_records(plans, records)['adjustments']['negative'], 1)

    def test_zero_and_sentinel_are_protected(self):
        for base in (0, -2559744, -2559745):
            plans, records = fixture()
            records[5, 1, 0].update(base=base, result=base, reason=2)
            self.assertEqual(audit_records(plans, records)['adjustments']['protected'], 1)

    def test_old_version_cannot_borrow_new_plan(self):
        plans, records = fixture()
        plans[6, 2] = plans.pop((5, 1))
        with self.assertRaisesRegex(ValueError, 'matching publication'):
            audit_records(plans, records)

    def test_wrong_arithmetic_and_mutating_observer_rejected(self):
        for index in (0, 2):
            plans, records = fixture()
            records[5, 1, index]['result'] += 1
            with self.assertRaises(ValueError):
                audit_records(plans, records)


if __name__ == '__main__':
    unittest.main()
