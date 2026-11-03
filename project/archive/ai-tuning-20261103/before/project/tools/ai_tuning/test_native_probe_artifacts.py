"""Pure artifact/staging regressions: no native/game/client actions."""
import json
import os
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import native_probe_artifacts as m

class ArtifactTests(unittest.TestCase):
    def test_partial_stage_restores_only_known_two_file_delta(self):
            self.exercise_stage_failure(unrelated_change=False)

    def test_partial_stage_preserves_unknown_unrelated_edit(self):
            self.exercise_stage_failure(unrelated_change=True)

    def exercise_stage_failure(self, unrelated_change):
            with tempfile.TemporaryDirectory(dir=os.environ.get("CSC_TEST_SCRATCH", tempfile.gettempdir())) as temporary:
                root=Path(temporary);repo=root/'repo';installed=root/'installed';deployment=root/'deployment';deployment.mkdir()
                for relative in m.RELATIVES:
                    source=repo/'Civ Supply Chains'/relative;source.parent.mkdir(parents=True,exist_ok=True);source.write_text('candidate '+relative)
                    target=installed/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('original '+relative)
                (installed/'unrelated.xml').write_text('original unrelated')
                def manifest(path):
                    return {str(p.relative_to(path)):dict(sha256=m.sha(p),size=p.stat().st_size)for p in path.rglob('*')if p.is_file()}
                def write(path,value):
                    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value))
                before=manifest(installed);original_replace=m.os.replace;calls=[]
                def replace(source,target):
                    calls.append(str(target))
                    self.assertTrue(all((deployment/'backup'/relative).exists()for relative in m.RELATIVES))
                    if len(calls)==2:
                        if unrelated_change:(installed/'unrelated.xml').write_text('human changed')
                        raise OSError('simulated second-file replacement failure')
                    original_replace(source,target)
                with patch.object(m.os,'replace',side_effect=replace):
                    with self.assertRaises((OSError,RuntimeError)):
                        m.stage_two_files(repo,installed,deployment,before,manifest,lambda:[],write)
                if unrelated_change:
                    self.assertEqual((installed/'unrelated.xml').read_text(),'human changed')
                    self.assertNotEqual(manifest(installed),before)
                    self.assertFalse((deployment/'partial-stage-restored.json').exists())
                else:
                    self.assertEqual(manifest(installed),before)
                    self.assertTrue((deployment/'partial-stage-restored.json').exists())

    def test_source_archive_excludes_binaries_and_large_json(self):
            with tempfile.TemporaryDirectory(dir=os.environ.get("CSC_TEST_SCRATCH", tempfile.gettempdir())) as temporary:
                root=Path(temporary)
                for name,content in [('script.lua',b'return true'),('game.exe',b'binary'),('source.Civ6Save',b'save'),('large.json',b'x'*(1024*1024+1))]:
                    (root/name).write_bytes(content)
                pins={str(p):m.sha(p)for p in root.iterdir()if p.is_file()}
                result=m.archive_sources(pins,root/'archive')
                self.assertEqual([Path(x['source']).name for x in result['archived']],['script.lua'])
                self.assertEqual(len(result['hash_path_only']),3)

class FourOverlayTests(unittest.TestCase):
    def setup_tree(self,root):
        installed=root/'installed';sources={};review={}
        for relative in m.FOUR_AI_RELATIVES:
            target=installed/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(('original '+relative).encode())
            source=root/'sources'/relative;source.parent.mkdir(parents=True,exist_ok=True);source.write_bytes(('candidate '+relative).encode());sources[relative]=source
            if relative in m.RELATIVES:review[relative]=source
        (installed/'unrelated.xml').write_text('preserve')
        return installed,sources,review

    @staticmethod
    def manifest(path):
        return {str(p.relative_to(path)):dict(sha256=m.sha(p),size=p.stat().st_size) for p in path.rglob('*')if p.is_file()}

    @staticmethod
    def write(path,value):
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value))

    def test_four_overlay_append_exact_prefix_and_restore(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('CSC_TEST_SCRATCH')) as d:
            root=Path(d);installed,sources,review=self.setup_tree(root);baseline=self.manifest(installed)
            sql=root/'trial.sql';sql.write_bytes(b'-- trial SQL');lua=root/'trial.lua';lua.write_bytes(b'-- trial Lua')
            overlay=m.compose_four_ai_overlay(installed,root/'overlay',baseline,review,sql,lua,self.write)
            for relative,payload in zip(m.FOUR_AI_RELATIVES[2:],(sql,lua)):
                self.assertEqual(Path(overlay[relative]).read_bytes(),(installed/relative).read_bytes()+b'\n'+payload.read_bytes())
            self.assertEqual(self.manifest(installed),baseline)
            deploy=root/'deployment';deploy.mkdir()
            expected=m.stage_four_ai_files(overlay,installed,deploy,baseline,self.manifest,lambda:[],self.write)
            self.assertEqual(len([k for k in expected if expected[k]!=baseline[k]]),4)
            m.restore_known_files(installed,deploy,baseline,expected,m.FOUR_AI_RELATIVES,self.manifest,lambda:[],self.write)
            self.assertEqual(self.manifest(installed),baseline)

    def test_four_partial_failure_restores_all_originals(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('CSC_TEST_SCRATCH')) as d:
            root=Path(d);installed,sources,_=self.setup_tree(root);baseline=self.manifest(installed);deploy=root/'deployment';deploy.mkdir()
            original=m.os.replace;calls=[]
            def replace(a,b):
                self.assertTrue(all((deploy/'backup'/r).is_file() for r in m.FOUR_AI_RELATIVES));calls.append(b)
                if len(calls)==3:raise OSError('third replacement fails')
                original(a,b)
            with patch.object(m.os,'replace',side_effect=replace):
                with self.assertRaises(OSError):m.stage_four_ai_files(sources,installed,deploy,baseline,self.manifest,lambda:[],self.write)
            self.assertEqual(self.manifest(installed),baseline)

    def test_four_scope_rejects_modinfo_or_unknown_restore(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('CSC_TEST_SCRATCH')) as d:
            root=Path(d);installed,sources,_=self.setup_tree(root);baseline=self.manifest(installed)
            with self.assertRaises(ValueError):m.stage_four_ai_files(dict(sources,**{'trial.modinfo':root/'x'}),installed,root/'deployment',baseline,self.manifest,lambda:[],self.write)
            with self.assertRaises(ValueError):m.restore_known_files(installed,root/'deployment',baseline,baseline,('trial.modinfo',),self.manifest,lambda:[],self.write)
            with self.assertRaises(RuntimeError):m.restore_known_files(installed,root/'deployment',baseline,baseline,m.FOUR_AI_RELATIVES,self.manifest,lambda:[123],self.write)


class ThreeOverlayTests(unittest.TestCase):
    setup_tree=FourOverlayTests.setup_tree
    manifest=staticmethod(FourOverlayTests.manifest)
    write=staticmethod(FourOverlayTests.write)
    def test_three_overlay_appends_only_SQL_and_Roles_exact_unchanged(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('CSC_TEST_SCRATCH'))as d:
            root=Path(d);installed,sources,review=self.setup_tree(root);baseline=self.manifest(installed)
            roles=installed/'ModSupport/ModSupport_RH_AI_Roles.lua';roles_bytes=roles.read_bytes();sql=root/'trial.sql';sql.write_bytes(b'--directtraittrial')
            overlay=m.compose_three_ai_overlay(installed,root/'overlay',baseline,review,sql,self.write)
            self.assertEqual(set(overlay),set(m.THREE_AI_RELATIVES));self.assertEqual(Path(overlay['ModSupport/ModSupport_RH_AI.sql']).read_bytes(),(installed/'ModSupport/ModSupport_RH_AI.sql').read_bytes()+b'\n'+sql.read_bytes())
            self.assertEqual(roles.read_bytes(),roles_bytes);deploy=root/'deployment';deploy.mkdir()
            expected=m.stage_three_ai_files(overlay,installed,deploy,baseline,self.manifest,lambda:[],self.write)
            self.assertEqual(len([key for key in baseline if baseline[key]!=expected[key]]),3);self.assertEqual(roles.read_bytes(),roles_bytes)
            self.assertFalse((deploy/'backup/ModSupport/ModSupport_RH_AI_Roles.lua').exists())
            m.restore_known_files(installed,deploy,baseline,expected,m.THREE_AI_RELATIVES,self.manifest,lambda:[],self.write)
            self.assertEqual(self.manifest(installed),baseline)
    def test_three_partial_third_replacement_failure_restores_only_approved(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('CSC_TEST_SCRATCH'))as d:
            root=Path(d);installed,sources,_=self.setup_tree(root);sources={key:sources[key]for key in m.THREE_AI_RELATIVES};before=self.manifest(installed);deploy=root/'deployment';deploy.mkdir()
            original=m.os.replace;calls=[]
            def replace(a,b):
                self.assertTrue(all((deploy/'backup'/r).exists()for r in m.THREE_AI_RELATIVES));calls.append(b)
                if len(calls)==3:raise OSError('third replacement fails')
                original(a,b)
            with patch.object(m.os,'replace',side_effect=replace):
                with self.assertRaises(OSError):m.stage_three_ai_files(sources,installed,deploy,before,self.manifest,lambda:[],self.write)
            self.assertEqual(self.manifest(installed),before)
    def test_three_scope_rejects_fourth_Roles_or_modinfo(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('CSC_TEST_SCRATCH'))as d:
            root=Path(d);installed,sources,_=self.setup_tree(root);before=self.manifest(installed)
            with self.assertRaises(ValueError):m.stage_three_ai_files(sources,installed,root/'deployment',before,self.manifest,lambda:[],self.write)
            exact={key:sources[key]for key in m.THREE_AI_RELATIVES};exact['trial.modinfo']=root/'modinfo'
            with self.assertRaises(ValueError):m.stage_three_ai_files(exact,installed,root/'deployment',before,self.manifest,lambda:[],self.write)
            self.assertEqual(self.manifest(installed),before)
    def test_unknown_Roles_edit_blocks_restoration_and_is_preserved(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('CSC_TEST_SCRATCH'))as d:
            root=Path(d);installed,sources,_=self.setup_tree(root);sources={key:sources[key]for key in m.THREE_AI_RELATIVES};before=self.manifest(installed);deploy=root/'deployment';deploy.mkdir()
            expected=m.stage_three_ai_files(sources,installed,deploy,before,self.manifest,lambda:[],self.write)
            roles=installed/'ModSupport/ModSupport_RH_AI_Roles.lua';roles.write_bytes(b'human edit after stage')
            with self.assertRaises(RuntimeError):m.restore_known_files(installed,deploy,before,expected,m.THREE_AI_RELATIVES,self.manifest,lambda:[],self.write)
            self.assertEqual(roles.read_bytes(),b'human edit after stage');self.assertFalse((root/'package-restored.json').exists())


if __name__ == "__main__":
    unittest.main()
