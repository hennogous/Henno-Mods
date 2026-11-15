"""Recovery evidence and menu-only lifecycle checks; no game or console access."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import planning_continue as continuation
import planning_interruption_reconcile as reconcile


class InterruptedLifecycle(unittest.TestCase):
    def test_reconciled_source_requires_its_own_cleanup_and_matching_original_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root/'source.json').write_text('{}')
            self.assertFalse(continuation.source_lifecycle_verified(root))
            record = dict(verified=True, original_exit_unknown=True, owners_absent=True,
                          preferences_verified=True, source=str(root), source_sha256=continuation.sha(root/'source.json'))
            (root/'interruption-reconciled.json').write_text(json.dumps(record))
            self.assertFalse(continuation.source_lifecycle_verified(root))
            (root/'interruption-cleanup').mkdir()
            (root/'interruption-cleanup/session-closed.json').write_text('{"verified":true}')
            self.assertTrue(continuation.source_lifecycle_verified(root))
            (root/'source.json').write_text('{"changed":true}')
            self.assertFalse(continuation.source_lifecycle_verified(root))

    def test_menu_cleanup_restores_before_archiving_and_never_loads_a_world(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve();source=root/'source';source.mkdir()
            binary=root/'game.exe';binary.write_bytes(b'fixture')
            (source/'source.json').write_text('{}')
            (source/'session-owner.json').write_text(json.dumps(dict(executable_path=str(binary),pid=123)))
            (source/'original-preferences.json').write_text('{}')
            (source/'resource-stack-preflight.json').write_text(json.dumps(dict(database=str(root/'Cache/DebugGameplay.sqlite'))))
            packages={}
            for role,name in [('CE','CSC Bakers Development CE'),('CSC','CSC Bakers Development Mod')]:
                frozen=root/'frozen'/role;frozen.mkdir(parents=True)
                installed=root/'Mods'/name;installed.mkdir(parents=True)
                packages[str(frozen)]=dict(install=str(installed),files={})
            (source/'packages.json').write_text(json.dumps(packages))
            events=[]
            class Session:
                def __init__(self,out,*args,**kwargs):self.out=out;self.owner=None;self.closed=False
                def start(self,callback):self.owner=callback();events.append('start-menu')
                def wait_context(self,name):assert name=='MainMenu';events.append('main-menu')
                def close(self,**callbacks):
                    callbacks['restore_preferences']();events.append('native-exit')
                    callbacks['restore_package']();events.append('archive-packages');self.closed=True
                    (self.out/'session-closed.json').write_text('{"verified":true}')
            def restore(controller,path):
                assert all(Path(row['install']).exists()for row in packages.values())
                events.append('restore-preferences')
                (path/'preferences-restored.json').write_text('{"verified":true}')
            owner=SimpleNamespace(poll=lambda:None)
            with patch.object(reconcile,'native_inventory',return_value=[]), \
                 patch.object(reconcile,'manifest',return_value={}), \
                 patch.object(reconcile,'sha',return_value=reconcile.HOTFIX_EXE_SHA), \
                 patch.object(reconcile,'make_probe_controller',return_value=object()), \
                 patch.object(reconcile,'NativeSession',Session), \
                 patch.object(reconcile,'launch',return_value=owner), \
                 patch.object(reconcile,'restore_preferences',side_effect=restore):
                reconcile.run(source)
            self.assertEqual(events,['start-menu','main-menu','restore-preferences','native-exit','archive-packages'])
            record=json.loads((source/'interruption-reconciled.json').read_text())
            self.assertTrue(record['original_exit_unknown'])
            self.assertFalse(record['gameplay_loaded'])
            self.assertEqual(record['AI_turns_advanced'],0)
            self.assertFalse((source/'session-closed.json').exists())
            self.assertTrue(all((source/Path(row['install']).name).exists()for row in packages.values()))

    def test_foreign_native_owner_blocks_before_any_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with patch.object(reconcile,'native_inventory',return_value=[{'pid':99}]):
                with self.assertRaisesRegex(RuntimeError,'owner remains'):
                    reconcile.run(root)
            self.assertFalse((root/'interruption-cleanup').exists())


if __name__ == '__main__':
    unittest.main()
