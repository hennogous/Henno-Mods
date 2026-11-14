"""Offline save-boundary evidence normalization; no game/controller imports."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

PATH = Path(__file__).with_name('planning_segments.py')
spec = importlib.util.spec_from_file_location('planning_segments', PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def write(root, name, value):
    path = root / name
    path.write_text(json.dumps(value) if not isinstance(value, str) else value, encoding='utf-8')


def fixture(root):
    original, continuation, output = (root / name for name in ('original', 'continuation', 'normalized'))
    original.mkdir(); continuation.mkdir()
    for folder in (original, continuation):
        write(folder, 'session-closed.json', {'verified': True})
        write(folder, 'preferences-restored.json', {'verified': True})
        write(folder, 'source.json', {'original_ai': [1, 2]})
        write(folder, 'protocol.json', {'fresh_game': folder == original, 'map': 'Pangaea'})
        write(folder, 'resource-stack-preflight.json', {'groups': {}})
    save = original / 'turn-200.Civ6Save'
    save.write_bytes(b'exact-save200-bytes')
    checkpoint = dict(verified=True, turn=200, unique_name='SAVE_200_exact', sha256=m.sha(save))
    write(original, 'checkpoint-200.json', checkpoint)
    write(continuation, 'continuation.json', dict(source=str(original), at=200, source_checkpoint=checkpoint))
    write(continuation, 'source-structure-comparison.json', {'verified': True})
    write(continuation, 'checkpoint.json', {'turn': 250})
    write(original, 'loaded-district-catalogue.txt', 'CSC_DISTRICT_CATALOGUE\t42\tDISTRICT_CSC_BAKERS_QUARTER')
    write(original, 'resource-origins.lua', '{}')
    for folder, turn, content in ((original, 200, 'retained-original'),
                                  (original, 205, 'abandoned'),
                                  (continuation, 200, 'duplicate-load-boundary'),
                                  (continuation, 205, 'retained-continuation')):
        write(folder, f'purchase-context-{turn}.txt', content)
    for turn in range(25, 251, 25):
        write(original if turn <= 200 else continuation, f'full-census-{turn}.json', {'turn': turn})
    write(original, 'Lua.log', '''noisy raw game line
CSC_PLANNING_FOUNDATION\tturn=12\tplot=100\tdistrict=42\tdistrictType=DISTRICT_CSC_BAKERS_QUARTER\tfoundationTurn=12\tsequence=7
CSC_PLANNING_COMPLETION\tturn=14\tplot=100\tdistrict=42\tcompletionTurn=14\tsequence=8
CSC_PLANNING_FOUNDATION\tturn=5\tplot=101\tdistrict=0\tdistrictType=DISTRICT_CITY_CENTER\tfoundationTurn=5\tcompletionTurn=5\tsequence=9
CSC_AI_QUARTER_COVERAGE turn=200 version=199 player=1 district=42 result={"staged":1,"masked":2}
CSC_QUARTER_WATCH_WRITE\tturn=200\tversion=199\tnativeOrdinal=17
CSC_EXACT_CHECKPOINT_COMPLETE\tSAVE_200_exact\ttrue
CSC_PLANNING_FOUNDATION\tturn=200\tplot=999\tdistrict=42\tsequence=900
CSC_AI_QUARTER_COVERAGE turn=200 version=200 player=1 district=42 result={"masked":999}
''')
    write(continuation, 'Lua.log', '''CSC_PLANNING_RELATION\tturn=200\tquarter=BAKERS\tquarterPlot=100\tneighbourPlot=101\tneighbourDistrict=0\tfoundationOrder=bothDatesUnknown\tcompletionOrder=bothDatesUnknown\tsequence=1
CSC_PLANNING_PLAN_TRANSITION\tturn=201\tsequence=2\treconsidered=false
CSC_AI_QUARTER_COVERAGE turn=201 version=1 player=1 district=42 result={"staged":1,"masked":3}
CSC_DISTRICT_UI_ADJACENCY\tturn=201\tplot=100\tavailable=true
''')
    for folder, rows in (
        (original, [dict(kind='district-selection', turn=199, sequence=1),
                    dict(kind='district-selection', turn=200, sequence=2),
                    dict(kind='district-selection', turn=205, sequence=3)]),
        (continuation, [dict(kind='district-selection', turn=200, sequence=1),
                        dict(kind='ready', sequence=2), dict(kind='district-selection', turn=250, sequence=3)]),
    ):
        write(folder, 'economy-savings.ndjson', ''.join(json.dumps(row)+'\n' for row in rows))
    return original, continuation, output


class SegmentTests(unittest.TestCase):
    def test_exact_marker_cut_native_gap_segments_and_physical_history(self):
        with tempfile.TemporaryDirectory(dir=PATH.parent) as tmp:
            original, continuation, output = fixture(Path(tmp))
            before = (original / 'Lua.log').read_bytes()
            result = m.merge(original, continuation, output)
            log = (output / 'Lua.log').read_text()
            self.assertNotIn('plot=999', log)
            self.assertNotIn('masked":999', log)
            self.assertNotIn('noisy raw', log)
            self.assertIn('CSC_PLANNING_MANAGED_COVERAGE', log)
            self.assertIn('nativeOrdinal=17\tsegment=original', log)
            self.assertIn('version=1\tplayer=1\tdistrict=42', log)
            self.assertIn('quarterFoundationTurn=12', log)
            self.assertIn('neighbourFoundationTurn=5', log)
            self.assertIn('recordedFoundationOrder=bothDatesUnknown', log)
            self.assertIn('foundationOrder=neighbourFirst', log)
            self.assertIn('completionOrder=neighbourFirst', log)
            self.assertIn('historySourceSegment=original', log)
            self.assertEqual(result['history_filled_relations'], 1)
            native = [json.loads(x) for x in (output / 'economy-savings.ndjson').read_text().splitlines()]
            self.assertEqual([(x['turn'], x['sequence'], x['segment']) for x in native],
                             [(199,1,'original'), (200,1,'continuation'), (250,3,'continuation')])
            self.assertEqual(result['native_excluded'], 3)
            self.assertEqual(result['native_coverage_gap']['turn'], 200)
            self.assertFalse(result['fresh_game']); self.assertFalse(result['uninterrupted'])
            self.assertFalse(m.load(output / 'protocol.json')['fresh_game'])
            self.assertEqual((original / 'Lua.log').read_bytes(), before)
            self.assertTrue((output / 'full-census-200.json').exists())
            self.assertTrue((output / 'full-census-250.json').exists())
            self.assertEqual(result['derived_manifest']['Lua.log'], m.sha(output / 'Lua.log'))
            self.assertEqual((output / 'purchase-context-original-200.txt').read_text(), 'retained-original')
            self.assertEqual((output / 'purchase-context-continuation-205.txt').read_text(), 'retained-continuation')
            self.assertFalse((output / 'purchase-context-original-205.txt').exists())
            self.assertFalse((output / 'purchase-context-continuation-200.txt').exists())
            self.assertEqual((original / 'purchase-context-205.txt').read_text(), 'abandoned')
            self.assertIn('purchase-context-continuation-205.txt', result['copies'])
            self.assertTrue(any('Storekeeper' in limit for limit in result['limits']))

    def test_active_input_wrong_marker_and_modified_checkpoint_are_rejected(self):
        for reason in ('active', 'marker', 'save'):
            with self.subTest(reason=reason), tempfile.TemporaryDirectory(dir=PATH.parent) as tmp:
                original, continuation, output = fixture(Path(tmp))
                if reason == 'active':
                    write(continuation, 'session-closed.json', {'verified': False})
                elif reason == 'marker':
                    write(original, 'Lua.log', 'CSC_EXACT_CHECKPOINT_COMPLETE\tWRONG_NAME\ttrue\n')
                else:
                    (original / 'turn-200.Civ6Save').write_bytes(b'changed')
                with self.assertRaises(ValueError):
                    m.merge(original, continuation, output)
                self.assertFalse(output.exists())

    def test_unknown_dates_stay_unknown_and_new_lifetimes_replace_old_history(self):
        history = {}
        unknown = dict(quarter='BAKERS', quarterPlot='100', neighbourPlot='101',
                       neighbourDistrict='0', foundationOrder='bothDatesUnknown')
        self.assertFalse(m._fill_relation(unknown, history))
        self.assertNotIn('historyFilled', unknown)
        for fields in (
            dict(plot='100', district='42', districtType='DISTRICT_CSC_BAKERS_QUARTER', foundationTurn='12', segment='original'),
            dict(plot='100', district='42', districtType='DISTRICT_CSC_BAKERS_QUARTER', foundationTurn='220', segment='continuation'),
        ):
            m._update_history(history, 'CSC_PLANNING_', 'FOUNDATION', fields)
        later = dict(unknown, neighbourFoundationTurn='200')
        self.assertTrue(m._fill_relation(later, history))
        self.assertEqual(later['quarterFoundationTurn'], '220')
        self.assertEqual(later['foundationOrder'], 'neighbourFirst')
        self.assertEqual(later['historySourceSegment'], 'continuation')
        m._update_history(history, 'CSC_PLANNING_', 'REMOVED', dict(plot='100', district='42'))
        self.assertFalse(history)


if __name__ == '__main__':
    unittest.main()
