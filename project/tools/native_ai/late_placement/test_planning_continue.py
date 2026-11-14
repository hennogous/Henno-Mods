"""Offline continuation gates/lifecycle; never launch or connect to a game."""
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import planning_continue as pc


class StructureTests(unittest.TestCase):
    def census(self):
        return dict(turn=200, rows=[['PLAYER', '1\ttrue'], ['CITY', '1\t7\t10\t99.5\t3'],
            ['QUARTER', 'BAKERS\t1\t7\t800\ttrue\tfalse\ttrue\t1\t2\t3'],
            ['PRODUCER', '800\t2\tBUILDING_CSC_BAKERS_WIND_MILL\t2'],
            ['MATERIAL', '800\t801\tBASE\tRESOURCE_WHEAT\ttrue'],
            ['CUSTOMER_HOST', '800\t802\tDISTRICT_CITY_CENTER\ttrue\tfalse'],
            ['CUSTOMER', '800\t802\t2\tDISTRICT_CITY_CENTER\ttrue\t2'],
            ['SERVICE_BUILDING', '1\t7\tBUILDING_CSC_BAKERS_STAGE_2_SERVICE\tfalse'],
            ['SALES', '800\t802\tDISTRICT_CITY_CENTER'], ['TREASURY', '1\t10\t5\t1'],
            ['ADJACENCY', 'BAKERS\t1\t7\t800\t2\t1\t2\t1'], ['END', '200\t11']])

    def test_structural_multiset_ignores_only_documented_outputs(self):
        before, after = self.census(), self.census()
        after['rows'][1][1] = '1\t7\t10\t125.25\t-2'
        after['rows'][2][1] = 'BAKERS\t1\t7\t800\ttrue\tfalse\ttrue\t0\t0\t0'
        after['rows'][-2][1] = 'BAKERS\t1\t7\t800\t2\t2\t2\t2'
        after['rows'].reverse()
        self.assertTrue(pc.compare_structure(before, after)['verified'])

    def test_population_material_building_and_customer_changes_are_rejected(self):
        for index, replacement in [(1, '1\t7\t9\t99.5\t3'),
                                   (3, '800\t2\tBUILDING_CSC_BAKERS_WIND_MILL\t1'),
                                   (4, '800\t801\tBASE\tRESOURCE_WHEAT\tfalse'),
                                   (5, '800\t802\tDISTRICT_CITY_CENTER\ttrue\ttrue')]:
            with self.subTest(index=index):
                before, after = self.census(), self.census()
                after['rows'][index][1] = replacement
                proof = pc.compare_structure(before, after)
                self.assertFalse(proof['verified'])
                self.assertTrue(proof['missing'] and proof['unexpected'])

    def test_duplicate_and_unknown_rows_are_not_silently_masked(self):
        before, after = self.census(), self.census()
        after['rows'].append(after['rows'][4])
        self.assertFalse(pc.compare_structure(before, after)['verified'])
        after['rows'].append(['NEW_UNKNOWN_STRUCTURE', 'x'])
        with self.assertRaisesRegex(RuntimeError, 'Unknown structural'):
            pc.compare_structure(before, after)

    def test_parser_requires_exact_clock_and_complete_row_count(self):
        raw='CSC_ENDPOINT_PLAYER\t1\ttrue\nCSC_ENDPOINT_CITY\t1\t7\t10\t2\t3\nCSC_ENDPOINT_END\t200\t2\n'
        self.assertEqual(pc.parse_census(raw,200)['turn'],200)
        for broken in (raw.replace('200\t2','199\t2'), raw.replace('200\t2','200\t3')):
            with self.assertRaisesRegex(RuntimeError,'Incomplete'):
                pc.parse_census(broken,200)


class ProvenanceTests(unittest.TestCase):
    def test_invalid_windows_fail_before_inventory_install_or_launch(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            for at,through in [(200,200),(200,300),(201,250)]:
                with patch.object(pc,'native_inventory') as inventory, patch.object(pc,'launch') as launch:
                    with self.assertRaisesRegex(RuntimeError,'Unsupported'):
                        pc.prepare(tmp,Path(tmp)/'new',at,through,tmp)
                    inventory.assert_not_called();launch.assert_not_called()

    def test_unclosed_source_and_external_policy_fail_before_checkpoint(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            with patch.object(pc,'load',return_value={'verified':False}), patch.object(pc,'sha') as sha:
                with self.assertRaisesRegex(RuntimeError,'close/restore'):
                    pc.prepare(tmp,Path(tmp)/'new',200,250,tmp)
                sha.assert_not_called()
            protocol={k:True for k in ('fresh_game','ordinary_setup','harmonised_observation',
                                      'planning_observation','passive_savings_observation')}
            protocol.update(untuned=False,external_policy=True,gameplay_interventions=False)
            def metadata(path):
                return protocol if path.name=='protocol.json' else {} if path.name=='source.json' else {'verified':True}
            with patch.object(pc,'load',side_effect=metadata), patch.object(pc,'sha') as sha:
                with self.assertRaisesRegex(RuntimeError,'integrated main CSC'):
                    pc.prepare(tmp,Path(tmp)/'new',200,250,tmp)
                sha.assert_not_called()

    def test_read_only_checkpoint_hash_gate_rejects_changed_save(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            protocol={k:True for k in ('fresh_game','ordinary_setup','harmonised_observation',
                                      'planning_observation','passive_savings_observation')}
            protocol.update(untuned=False,external_policy=False,gameplay_interventions=False,
                            map='Pangaea',map_seed=18431267,game_seed=28681391)
            identity=dict(original_ai=[1,2,3,4,5],map_signature=[74,46,1],
                          starts=[{'player':p} for p in range(6)])
            checkpoint=dict(verified=True,turn=200,native_save='changed.Civ6Save',archive='old.Civ6Save',sha256='expected')
            def metadata(path):
                return {'protocol.json':protocol,'source.json':identity,'checkpoint-200.json':checkpoint}.get(path.name,{'verified':True})
            with patch.object(pc,'load',side_effect=metadata), patch.object(pc,'sha',return_value='different'):
                with self.assertRaisesRegex(RuntimeError,'hash mismatch'):
                    pc.prepare(tmp,Path(tmp)/'new',200,250,tmp)


class LifecycleTests(unittest.TestCase):
    def test_shared_session_load_once_and_exit_detach_order_without_game_access(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root=Path(tmp);out=root/'continued';user=root/'user';user.mkdir()
            events=[];owner=SimpleNamespace(pid=123,exited=False)
            owner.poll=lambda:0 if owner.exited else None
            identity=dict(original_ai=[1,2,3,4,5],map_signature=[74,46,1],
                          starts=[dict(player=p,leader='LEADER_'+str(p)) for p in range(6)])
            expected=dict(turn=200,rows=[['PLAYER','1\ttrue']])
            packages=[dict(source=root/role,install=root/('installed-'+role),files={},id=role,role=role) for role in ('ce','csc')]
            plan=pc.ContinuationPlan(root,out,200,250,root,
                dict(ce='ce',csc='csc',map='Pangaea',map_seed=1,game_seed=2,interval_minutes=15),
                identity,dict(native_save=str(root/'source.Civ6Save'),sha256='pinned'),expected,
                packages,{'a':{},'b':{},'c':{}},root/'game.exe',user,root)
            def command(code,context,label):
                if label=='continuation-source-identity':
                    return 'CSC_CONTINUATION_GRID=[74,46]\nCSC_CONTINUATION_NATIVE={"ready":1,"faults":0,"enabled":1,"version":1}'
                if label=='continuation-source-census':
                    return 'CSC_ENDPOINT_PLAYER\t1\ttrue\nCSC_ENDPOINT_END\t200\t1\n'
                if label=='install-continuation-storekeeper-watch':return 'CSC_BAKERS_STOREKEEPER_WATCH_INSTALLED'
                return 'CSC_CONTINUATION_END={"ready":1,"faults":0,"enabled":1,"version":1}'
            controller=SimpleNamespace(cmd=command)
            class Session:
                def __init__(self,*args,**kwargs):self.owner=None;self.closed=False
                def start(self,callback):self.owner=callback();events.append('started')
                def wait_context(self,*args):pass
                def issue_once(self,*args):events.append('enable')
                def load_once(self,*args,**kwargs):events.append('load-once');kwargs['eligibility']()
                def close(self,**callbacks):
                    callbacks['before_menu']();events.append('menu');callbacks['restore_preferences']()
                    owner.exited=True;events.append('native-exit');callbacks['after_native_exit']()
                    callbacks['restore_package']();self.closed=True;events.append('held-close')
            watch=Mock()
            watch.freeze.side_effect=lambda:events.append('freeze')
            def detached():
                self.assertEqual(owner.poll(),0);events.append('detach')
            watch.after_exit.side_effect=detached
            def modules(*args):
                pc.write_json(out/'loaded-modules.json',{'GameCore_XP2_FinalRelease.dll':{'path':'qualified.dll'}})
            def install(*args,**kwargs):
                (out/'loaded-district-catalogue.txt').write_text('CSC_DISTRICT_CATALOGUE\t43\tTAILORS\n')
            def copytree(source,destination):destination.mkdir()
            with patch.object(pc,'prepare',return_value=plan), patch.object(pc,'native_inventory',return_value=[]), \
                 patch.object(pc,'make_probe_controller',return_value=controller), patch.object(pc,'NativeSession',Session), \
                 patch.object(pc,'launch',return_value=owner), patch.object(pc,'configure'), \
                 patch.object(pc,'flags',return_value={'mods':{k:True for k in ['ce','csc','a','b','c']}}), \
                 patch.object(pc,'verify_modules',side_effect=modules), patch.object(pc,'manifest',return_value={}), \
                 patch.object(pc,'archive_sources',return_value={}), patch.object(pc.shutil,'copytree',side_effect=copytree), \
                 patch.object(pc,'save_inactive_boundary',return_value={'verified':True}), patch.object(pc,'capture_census'), \
                 patch.object(pc,'summarize_run') as summary, patch('full_game_observation.install',side_effect=install), \
                 patch('full_game_observation.play') as play, patch('full_game_observation.finish') as finish, \
                 patch('economy_preflight.inspect'), patch('economy_savings_watch.EconomySavingsWatch',return_value=watch):
                # Extras normally hold pinned files. This fixture supplies their
                # minimal fields only after constructing its exact five IDs.
                for item in plan.extras.values():item.update(path=str(root),files={})
                pc.run(SimpleNamespace(source=root,output=out,at=200,through=250,dependencies=root))
            self.assertEqual(events.count('load-once'),1)
            self.assertLess(events.index('freeze'),events.index('menu'))
            self.assertLess(events.index('native-exit'),events.index('detach'))
            self.assertLess(events.index('detach'),events.index('held-close'))
            self.assertEqual(summary.call_args.args[2:4],(200,250))
            finish.assert_called_once_with(out,250,start=200)
            self.assertEqual(play.call_args.kwargs['start'],200)
            self.assertTrue((out/'source-structure-comparison.json').is_file())
            self.assertFalse(pc.load(out/'protocol.json')['fresh_game'])
            watch.qualify.assert_called_once()


if __name__=='__main__':
    unittest.main()
