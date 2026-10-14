"""The normal entry point installs only after a successful conversion."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('asset_runner', Path(__file__).resolve().parents[1] / 'export_assets.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RunnerTests(unittest.TestCase):
    def test_previous_setup_uses_successful_matching_mod_and_skips_failed_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def snapshot(name, status, mod, blockers=()):
                out = root / 'export-runs' / name
                out.mkdir(parents=True)
                (out / 'export-setup.json').write_text(json.dumps({
                    'schema_version': 1, 'mod_root': str(mod), 'has_contract': True}))
                (out / 'export.defaults.json').write_text('{}')
                (out / 'export-contract.json').write_text('{}')
                (out / 'report.json').write_text(json.dumps({'status': status, 'blockers': list(blockers)}))
                return out
            valid = snapshot('01', 'converted_pending_asset_editor_and_game_review', root / 'mod')
            snapshot('02', 'installed_pending_asset_editor_and_game_review', root / 'other-mod')
            snapshot('03', 'ready_for_windows_conversion', root / 'mod', ['bad geometry'])
            snapshot('04', 'purged', root / 'mod')
            self.assertEqual(runner.previous_setup(root, root / 'mod'),
                             (valid / 'export.defaults.json', valid / 'export-contract.json'))
            (valid / 'export-contract.json').unlink()
            self.assertEqual(runner.previous_setup(root, root / 'mod'), (None, None))

    def test_revision_defaults_and_explicit_override_precedence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(runner.defaults_path(None,root,root/'helpers'),root/'helpers/csc.defaults.json')
            local = root/'export.defaults.json';local.write_text('{}')
            self.assertEqual(runner.defaults_path(None,root,root/'helpers'),local)
            explicit = root/'explicit.json'
            self.assertEqual(runner.defaults_path(explicit,root,root/'helpers'),explicit)

    def run_export(self, flags=(), fail_conversion=False):
        calls = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('mod', 'library', 'blends'):
                (root / name).mkdir()
            (root / 'library/catalogue.json').write_text(json.dumps({'assets': []}))
            (root / 'blends/source.blend').touch()
            argv = ['export_assets.py', '--mod-root', str(root / 'mod'),
                    '--library', str(root / 'library'), '--blend-directory', str(root / 'blends'), *flags]

            def step(command, log):
                calls.append(log.stem)
                if log.stem == 'discover':
                    Path(command[-1]).write_text('[]')
                if fail_conversion and log.stem == 'convert':
                    raise RuntimeError('conversion failed')

            with patch.object(sys, 'argv', argv), patch.object(runner, 'executable', side_effect=lambda x: x), \
                 patch.object(runner, 'run_step', side_effect=step), \
                 patch('discovery.make_job', return_value=({}, {'blockers': []})):
                if fail_conversion:
                    with self.assertRaisesRegex(RuntimeError, 'conversion failed'):
                        runner.main()
                else:
                    self.assertEqual(runner.main(), 0)
        return calls

    def test_default_installs_after_conversion(self):
        self.assertEqual(self.run_export(), ['discover', 'decode', 'build', 'convert', 'install'])

    def test_no_install_still_converts(self):
        self.assertEqual(self.run_export(['--no-install']), ['discover', 'decode', 'build', 'convert'])

    def test_stage_only_does_not_convert_or_install(self):
        self.assertEqual(self.run_export(['--stage-only']), ['discover', 'decode', 'build'])

    def test_failed_conversion_never_installs(self):
        self.assertEqual(self.run_export(fail_conversion=True), ['discover', 'decode', 'build', 'convert'])

    def test_latest_installed_job_ignores_superseded_and_uninstalled_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            blends=Path(directory); runs=blends/'export-runs'
            for name,status in [('20260101','superseded'),('20260102','installed_pending_asset_editor_and_game_review'),
                                ('20260103','uninstalled')]:
                folder=runs/name; folder.mkdir(parents=True)
                (folder/'job.json').write_text(json.dumps({'output':str(folder)}))
                (folder/'report.json').write_text(json.dumps({'status':status}))
            with self.assertRaisesRegex(ValueError,'No installed export run'):
                runner.latest_installed_job(blends)
            (runs/'20260103/report.json').write_text(json.dumps({
                'status':'converted_pending_asset_editor_and_game_review'}))
            self.assertEqual(runner.latest_installed_job(blends),runs/'20260102/job.json')
