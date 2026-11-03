import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(os.environ.get('CSC_TEST_SCRATCH',tempfile.gettempdir()))
import native_probe_artifacts as m
def manifest(root):return {str(p.relative_to(root)):{'sha256':m.sha(p),'size':p.stat().st_size}for p in root.rglob('*')if p.is_file()}
def write(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value))

class ArtifactV2Tests(unittest.TestCase):
    def setup_files(self,root):
        installed=root/'installed';installed.mkdir();replacement={}
        for i,relative in enumerate(m.V2_FIVE_AI_RELATIVES):
            p=installed/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(('original'+str(i)).encode())
            if relative!='ModSupport/ModSupport_RH_AI.sql':
                p=root/('source'+str(i));p.write_bytes(('replacement'+str(i)).encode());replacement[relative]=p
        (installed/'art.txt').write_bytes(b'untouched');append=root/'direct.sql';append.write_bytes(b'unchangedGranaryPayload')
        return installed,replacement,append,manifest(installed)

    def test_compose_five_exact_replacements_append_no_roles(self):
        with tempfile.TemporaryDirectory(dir=HERE)as td:
            root=Path(td);installed,replacement,append,baseline=self.setup_files(root)
            result=m.compose_v2_ai_overlay(installed,root/'overlay',baseline,replacement,append,write)
            self.assertEqual(set(result),set(m.V2_FIVE_AI_RELATIVES));self.assertEqual(manifest(installed),baseline)
            for relative,path in result.items():self.assertEqual(Path(path).read_bytes(),(installed/relative).read_bytes()+b'\n'+append.read_bytes()if relative.endswith('RH_AI.sql')else replacement[relative].read_bytes())
            with self.assertRaises(ValueError):m.compose_v2_ai_overlay(installed,root/'bad',baseline,dict(replacement,**{'ModSupport/ModSupport_RH_AI_Roles.lua':append}),append,write)

    def test_full_stage_restore_and_all_backups_before_replace(self):
        with tempfile.TemporaryDirectory(dir=HERE)as td:
            root=Path(td);installed,replacement,append,baseline=self.setup_files(root);overlay=m.compose_v2_ai_overlay(installed,root/'overlay',baseline,replacement,append,write);deployment=root/'deployment';deployment.mkdir();real=m.os.replace
            def replace(src,dst):
                self.assertTrue(all((deployment/'backup'/r).exists()for r in m.V2_FIVE_AI_RELATIVES));return real(src,dst)
            with patch.object(m.os,'replace',side_effect=replace):expected=m.stage_v2_ai_files(overlay,installed,deployment,baseline,manifest,lambda:[],write)
            self.assertEqual(manifest(installed),expected);self.assertEqual((installed/'art.txt').read_bytes(),b'untouched')
            m.restore_known_files(installed,deployment,baseline,expected,m.V2_FIVE_AI_RELATIVES,manifest,lambda:[],write);self.assertEqual(manifest(installed),baseline)

    def test_wrong_scope_or_live_owner_cannot_stage(self):
        with tempfile.TemporaryDirectory(dir=HERE)as td:
            root=Path(td);installed,replacement,append,baseline=self.setup_files(root);deployment=root/'deployment';deployment.mkdir()
            with self.assertRaises(ValueError):m.stage_v2_ai_files(replacement,installed,deployment,baseline,manifest,lambda:[],write)
            overlay=m.compose_v2_ai_overlay(installed,root/'overlay',baseline,replacement,append,write)
            with self.assertRaisesRegex(RuntimeError,'unknown owner/bytes preserved'):m.stage_v2_ai_files(overlay,installed,deployment,baseline,manifest,lambda:[{'pid':1}],write)
            self.assertEqual(manifest(installed),baseline)

    def test_partial_failure_restores_only_known_bytes(self):
        with tempfile.TemporaryDirectory(dir=HERE)as td:
            root=Path(td);installed,replacement,append,baseline=self.setup_files(root);overlay=m.compose_v2_ai_overlay(installed,root/'overlay',baseline,replacement,append,write);deployment=root/'deployment';deployment.mkdir();real=m.os.replace;calls=[]
            def replace(src,dst):
                calls.append(dst)
                if len(calls)==3:raise OSError('simulated third replacement failure')
                return real(src,dst)
            with patch.object(m.os,'replace',side_effect=replace),self.assertRaisesRegex(OSError,'third replacement'):m.stage_v2_ai_files(overlay,installed,deployment,baseline,manifest,lambda:[],write)
            self.assertEqual(manifest(installed),baseline)

    def test_legacy_scopes_are_unchanged(self):
        self.assertEqual(len(m.RELATIVES),2);self.assertEqual(len(m.THREE_AI_RELATIVES),3);self.assertEqual(len(m.FOUR_AI_RELATIVES),4)
        self.assertIn('ModSupport/ModSupport_RH_AI_Roles.lua',m.FOUR_AI_RELATIVES);self.assertNotIn('Lua_UI/AI/CSC_AI_AssistanceUI.lua',m.FOUR_AI_RELATIVES)
        self.assertNotIn('ModSupport/ModSupport_RH_AI_Roles.lua',m.V2_FIVE_AI_RELATIVES)

if __name__=='__main__':unittest.main()
