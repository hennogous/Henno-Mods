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
