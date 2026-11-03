"""Real probe adapter/finite-core integration; no sockets, native app or installs."""
import ast
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from . import controller as control
from . import probe


class ProbeTests(unittest.TestCase):
    scratch = None

    def setUp(self):
        parent = Path(self.scratch or tempfile.gettempdir()).resolve()
        self.temp = tempfile.TemporaryDirectory(prefix='csc-probe-', dir=parent)
        self.root = Path(self.temp.name).resolve()
        assert self.root.parent == parent, 'Temporary cleanup target escaped its parent'
        self.addCleanup(self.temp.cleanup)
        self.user = self.root / 'native-user'
        (self.user / 'Logs').mkdir(parents=True)
        self.output = self.root / 'output'
        self.transmissions = []
        self.guards = []

    def runner(self, log=None, reply='CSC_OBSERVER_WARNING_DISMISS_REQUESTED 121 5 5 0'):
        if log is not None:
            (self.user / 'Logs/DiplomacyManager.csv').write_text(log, encoding='utf-8')
        discovery = lambda required: (4318, {'GameCore_Tuner': 1, 'DiplomacyActionView': 2})
        with patch.object(probe, 'discover_contexts', discovery):
            runner = probe.make_probe_controller(self.output, user_root=self.user)
        runner.game_pid = 14068
        runner.allow_observer_warning_dismissal = True

        def receive(code, state, token, port, **kwargs):
            self.transmissions.append((code, state, token, port))
            if code == control.HANDOFF:
                return 'CSC_SHARED_STATE 121 true 1 -1 false true', True
            self.guards.append(code)
            if isinstance(reply, Exception):
                raise reply
            return reply, True

        self.addCleanup(patch.stopall)
        patch.object(control, 'receive_command', receive).start()
        return runner

    def test_real_probe_passive_warning_reaches_guard_once_with_native_user_root(self):
        runner = self.runner('121,5,0,5,DIPLOMATIC_HIDDEN_AGENDA_WARNING,NONE,INITIAL\n')
        runner.dismiss_observer_warning(122)
        runner.dismiss_observer_warning(122)
        self.assertEqual(runner.diagnostics.USER, self.user.resolve())
        self.assertEqual(len(self.guards), 1)
        code = self.guards[0]
        self.assertIn('local from=5', code)
        self.assertIn('local turn=121;local target=122', code)
        self.assertIn('DiplomacyManager.FindOpenSessionID(0,from)', code)
        self.assertIn('DiplomacyManager.CloseSession(id)', code)
        self.assertNotIn('__', code)
        self.assertNotIn('AddResponse(', code)
        self.assertNotIn('SetTurns(', code)
        journal = [json.loads(row) for row in (self.output/'controller-journal.ndjson').read_text().splitlines()]
        self.assertEqual(sum(row['event']=='observer-warning-dismissal-begin' for row in journal), 1)
        receipts = list((self.output/'session-dismissals').glob('*.json'))
        self.assertEqual(len(receipts), 1)
        self.assertTrue(json.loads(receipts[0].read_text())['requested'])

    def test_real_probe_unknown_recent_deal_or_no_matching_log_has_no_guard(self):
        cases = (None, '', '121,5,0,5,UNKNOWN_STATEMENT\n',
                 '121,5,0,5,DIPLOMATIC_HIDDEN_AGENDA_WARNING\n121,5,0,5,MAKE_DEAL\n',
                 '120,5,0,5,DIPLOMATIC_HIDDEN_AGENDA_WARNING\n',
                 '121,5,1,5,DIPLOMATIC_HIDDEN_AGENDA_WARNING\n')
        for text in cases:
            with self.subTest(log=text):
                # Each runner's evidence stays in its own child directory.
                self.output = self.root / ('output-' + str(len(self.transmissions)))
                if text is None:
                    self.assertFalse((self.user/'Logs/DiplomacyManager.csv').exists())
                runner = self.runner(text)
                runner.dismiss_observer_warning(122)
                self.assertEqual(self.guards, [])
                self.assertTrue(all(code == control.HANDOFF for code, *_ in self.transmissions))

    def test_real_probe_ambiguous_guard_transmission_is_not_resent(self):
        runner = self.runner('121,5,0,5,DIPLOMATIC_HIDDEN_AGENDA_WARNING\n', OSError('ambiguous send'))
        with self.assertRaisesRegex(OSError, 'ambiguous send'):
            runner.dismiss_observer_warning(122)
        runner.dismiss_observer_warning(122)
        self.assertEqual(len(self.guards), 1)

    def test_real_diagnostics_satisfies_every_controller_attribute_consumption(self):
        runner = probe.make_probe_controller(self.output, user_root=self.user)
        tree = ast.parse(Path(control.__file__).read_text(encoding='utf-8'))
        consumed = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
                    and isinstance(node.value, ast.Attribute) and node.value.attr == 'diagnostics'
                    and isinstance(node.value.value, ast.Name) and node.value.value.id == 'self'}
        self.assertIn('USER', consumed)
        for name in consumed:
            with self.subTest(attribute=name):
                self.assertTrue(hasattr(runner.diagnostics, name))
                if name != 'USER': self.assertTrue(callable(getattr(runner.diagnostics, name)))
        runner.diagnostics.checkpoint('contract-test')
        value = self.output/'diagnostic.json'
        runner.diagnostics.write(value, {'verified':True})
        self.assertEqual(len(runner.diagnostics.sha(value)), 64)

    def test_default_localappdata_requires_existing_native_logs_directory(self):
        local = self.root/'local'
        expected = local/'Firaxis Games'/"Sid Meier's Civilization VI"
        (expected/'Logs').mkdir(parents=True)
        with patch.dict(os.environ, {'LOCALAPPDATA':str(local)}):
            runner = probe.make_probe_controller(self.output)
        self.assertEqual(runner.diagnostics.USER, expected.resolve())

    def test_missing_or_redirected_default_never_falls_back_to_output(self):
        for value in (None, 'relative-local', str(self.root/'sandbox-local')):
            with self.subTest(localappdata=value):
                with patch.dict(os.environ, {}, clear=True):
                    if value is not None: os.environ['LOCALAPPDATA'] = value
                    with self.assertRaisesRegex(ValueError, 'Pass user_root explicitly'):
                        probe.make_probe_controller(self.output)

    def test_explicit_user_root_is_authoritative_and_validated(self):
        with patch.dict(os.environ, {'LOCALAPPDATA':str(self.root/'wrong-local')}):
            diagnostics = probe.Diagnostics(self.output, user_root=self.user)
        self.assertEqual(diagnostics.USER, self.user.resolve())
        for value in ('relative-user', self.root/'missing-user'):
            with self.subTest(root=value):
                with self.assertRaisesRegex(ValueError, 'absolute existing'):
                    probe.Diagnostics(self.output, user_root=value)


if __name__ == '__main__': unittest.main()
