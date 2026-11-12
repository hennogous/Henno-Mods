"""Census totals count Quarters, not deposits, and preserve missing evidence."""
from pathlib import Path
import json
import tempfile
import unittest
from full_game_results import summarize,economy,census,compare


class Results(unittest.TestCase):
    def sample(self,folder):
        rows=[['PLAYER','1\ttrue'],['TREASURY','1\t100\t30\t3'],
            ['CITY','1\t42\t10\t15\t5'],
            ['QUARTER','BAKERS\t1\t42\t100\ttrue\tfalse\ttrue\t1\t0\t0'],
            ['MATERIAL','100\t101\tBASE\tRESOURCE_TEST\ttrue'],
            ['MATERIAL','100\t102\tBASE\tRESOURCE_TEST\ttrue'],
            ['MATERIAL','100\t103\tSPEC\tRESOURCE_SPEC\tfalse'],
            ['PRODUCER','100\t2\tBUILDING_TEST\t2'],
            ['CUSTOMER','100\t99\t2\tDISTRICT_CITY_CENTER\ttrue\t2'],
            ['END','200\t9']]
        path=Path(folder)/'census.json'
        path.write_text(json.dumps(dict(turn=200,phase='turn-start',rows=rows)),encoding='utf-8')
        return path

    def test_materials_count_quarters_and_physical_chain_is_distinct(self):
        with tempfile.TemporaryDirectory()as folder:
            result=summarize(self.sample(folder))['BAKERS']
            self.assertEqual([result[k]for k in('complete','base','base_improved','both','stage2_physical','service2_property')],[1,1,1,1,1,1])
            self.assertEqual(result['both_improved'],0)

    def test_economy_reports_gross_and_net_separately(self):
        with tempfile.TemporaryDirectory()as folder:
            total,players=economy(self.sample(folder))
            self.assertEqual((total['players'],total['production'],total['net_gold'],total['food']),(1,15,27,5))

    def test_partial_footer_cannot_be_used_as_comparison_data(self):
        with tempfile.TemporaryDirectory()as folder:
            path=self.sample(folder);data=json.loads(path.read_text());data['rows'].pop()
            path.write_text(json.dumps(data))
            with self.assertRaises(AssertionError):census(path)

    def comparison(self,folder,*,eliminated=False):
        root=Path(folder);run=root/'run';old=root/'old';run.mkdir();old.mkdir()
        template=json.loads(self.sample(folder).read_text())
        def write(path,value):path.write_text(json.dumps(value),encoding='utf-8')
        def sample(path,turn,dead=False):
            rows=([['PLAYER','1\tfalse']]if dead else template['rows'][:-1])+[['PLAYER','2\tfalse']]
            write(path,dict(turn=turn,phase='turn-start',rows=rows+[['END',str(turn)+'\t'+str(len(rows))]]))
        source=dict(original_ai=[1,2],map_signature=[74,46,1],starts=[],units=[])
        protocol=dict(map='Continents',map_size='small',map_seed=1,game_seed=2)
        for path in(run,old):write(path/'source.json',source);write(path/'protocol.json',protocol)
        write(run/'result.json',dict(closed=True,reached=250,storekeeper={}))
        write(run/'session-closed.json',dict(verified=True))
        write(run/'full-game-observation-complete.json',dict(verified=True))
        (run/'Lua.log').write_text('CSC_AI_BAKERS_DISTRICTS turn=1 version=1 players=2 entries=0 omitted=0 previousMatched=0 previousChanged=0\n')
        baseline=root/'baseline.json';sample(baseline,200)
        for turn in range(25,251,25):sample(run/('full-census-'+str(turn)+'.json'),turn,eliminated)
        return run,baseline,old

    def test_comparison_uses_original_seats_and_handles_elimination(self):
        with tempfile.TemporaryDirectory()as folder:
            run,baseline,old=self.comparison(folder,eliminated=True)
            result=compare(run,baseline,old)
            self.assertEqual(result['windows']['baseline200']['average_per_original_ai']['production'],7.5)
            current=result['windows']['harmonised200']
            self.assertEqual(current['average_per_original_ai']['production'],0)
            self.assertIsNone(current['average_per_city']['production'])
            self.assertEqual(current['economy']['players'],0)

    def test_comparison_rejects_wrong_window_even_with_valid_footer(self):
        with tempfile.TemporaryDirectory()as folder:
            run,baseline,old=self.comparison(folder)
            path=run/'full-census-200.json';value=json.loads(path.read_text())
            value['turn']=199;value['rows'][-1][1]='199\t10';path.write_text(json.dumps(value))
            with self.assertRaisesRegex(AssertionError,'comparison-window'):compare(run,baseline,old)

    def test_mismatched_initial_state_is_not_labelled_same_seed(self):
        with tempfile.TemporaryDirectory()as folder:
            run,baseline,old=self.comparison(folder)
            path=old/'source.json';value=json.loads(path.read_text());value['map_signature']=[74,46,2]
            path.write_text(json.dumps(value))
            self.assertNotIn('same-seed',compare(run,baseline,old)['comparison'])
            value['original_ai']=[1];path.write_text(json.dumps(value))
            with self.assertRaisesRegex(AssertionError,'cohorts'):compare(run,baseline,old)

    def test_cityless_survivor_has_zero_city_output(self):
        with tempfile.TemporaryDirectory()as folder:
            path=Path(folder)/'cityless.json'
            path.write_text(json.dumps(dict(turn=200,rows=[['PLAYER','1\ttrue'],
                ['TREASURY','1\t0\t0\t0'],['END','200\t2']])))
            total,players=economy(path)
            self.assertEqual((total['players'],total['cities'],total['production']),(1,0,0))


if __name__=='__main__':unittest.main()
