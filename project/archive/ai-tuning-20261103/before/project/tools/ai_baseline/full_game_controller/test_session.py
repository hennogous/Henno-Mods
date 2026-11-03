"""Failure-path tests with no native connections or installed writes."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from .session import NativeSession, SessionError
from .transport import MissingAcknowledgment, NativeLuaFailure
from .probe import make_probe_controller, write_json


class Owner:
    pid = 73
    identity = dict(pid=73, creation_filetime=123, executable_path='native.exe')
    code = None
    def poll(self): return self.code
    def close(self): self.closed = True


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name)
        self.owner = Owner()
        self.rows = []
        self.contexts = {'MainMenu': 1}
        self.r = Mock()
        self.time = 0
        self.s = NativeSession(self.out, self.r, inventory=lambda:self.rows,
                               hold=lambda pid:self.owner, write=write_json,
                               discover=lambda **kw:(4318,self.contexts),
                               clock=lambda:self.time, sleep=self.sleep)
        self.launch = Mock(return_value=self.owner)

    def sleep(self, seconds): self.time += seconds
    def start(self): self.s.start(self.launch)
    def save(self):
        source = self.out/'source.Civ6Save'
        source.write_bytes(b'CIV6 test bytes')
        return source,hashlib.sha256(source.read_bytes()).hexdigest()
    def exit_on_request(self, code, context, label, **kw):
        if label == 'exit': self.owner.code = 0

    def test_foreign_owner_never_launches(self):
        self.rows = [{'pid':99}]
        with self.assertRaises(SessionError): self.start()
        self.launch.assert_not_called()

    def test_attach_requires_sole_declared_owner(self):
        self.rows = [{'pid':99}]
        with self.assertRaises(SessionError): self.s.start(attach_pid=73)

    def test_attach_holds_identity_without_launch(self):
        self.rows = [{'pid':73,'identity':self.owner.identity}]
        self.s.start(attach_pid=73)
        self.assertEqual(self.r.game_pid,73)
        self.assertEqual(json.loads((self.out/'session-owner.json').read_text()),self.owner.identity)

    def test_attach_pid_replacement_between_inventory_and_hold_is_rejected(self):
        self.rows = [dict(pid=73,identity=dict(self.owner.identity,creation_filetime=1))]
        with self.assertRaises(SessionError): self.s.start(attach_pid=73)
        self.r.cmd.assert_not_called()

    def test_launched_held_identity_is_reused_not_reopened(self):
        self.s.hold = Mock(side_effect=AssertionError('must not reopen PID'))
        self.start()
        self.s.hold.assert_not_called()

    def test_exited_held_owner_cannot_reach_context(self):
        self.start();self.owner.code = 0
        with self.assertRaises(SessionError): self.s.wait_context('MainMenu')

    def test_pid_reuse_inventory_does_not_revive_held_owner(self):
        self.start();self.owner.code = 0;self.rows = [{'pid':73,'creation':'new'}]
        with self.assertRaises(SessionError): self.s.wait_context('MainMenu')

    def test_load_ack_is_not_context_readiness(self):
        self.start();source,digest = self.save()
        with self.assertRaises(TimeoutError):
            self.s.load_once(source,sha256=digest,native_directory=self.out,turn=110,
                             contexts=('GameCore_Tuner',),eligibility=lambda:True,timeout=1)
        self.assertFalse(self.s.eligible)
        self.assertEqual(self.r.cmd.call_count,1)

    def test_complete_source_mismatch_blocks_eligibility(self):
        self.start();source,digest = self.save()
        with self.assertRaises(SessionError):
            self.s.load_once(source,sha256=digest,native_directory=self.out,turn=110,
                             contexts=('MainMenu',),eligibility=lambda:False)
        self.assertFalse(self.s.eligible)
        self.assertFalse((self.out/'session-source-ready.json').exists())

    def test_successful_source_records_gate_after_ready(self):
        self.start();source,digest = self.save()
        self.s.load_once(source,sha256=digest,native_directory=self.out,turn=110,
                         contexts=('MainMenu',),eligibility=lambda:True)
        self.assertTrue(self.s.eligible)
        self.assertEqual(self.r.last_interval_turn,110)
        self.r.ready.assert_called_once_with(110,'session-source-ready')

    def test_input_hash_fails_before_load(self):
        self.start();source,_ = self.save()
        with self.assertRaises(SessionError):
            self.s.issue_load_once(source,sha256='wrong',native_directory=self.out,turn=110)
        self.r.cmd.assert_not_called()

    def test_unsupported_desktop_path_fails_before_load(self):
        self.start();source,digest = self.save()
        with self.assertRaises(SessionError):
            self.s.issue_load_once(source,sha256=digest,native_directory=self.out/'Single',turn=110)
        self.r.cmd.assert_not_called()

    def test_ambiguous_load_never_resends_even_new_session(self):
        self.start();source,digest = self.save()
        self.r.cmd.side_effect = MissingAcknowledgment('load','partial')
        self.s.issue_load_once(source,sha256=digest,native_directory=self.out,turn=110)
        with self.assertRaises(FileExistsError):
            self.s.issue_load_once(source,sha256=digest,native_directory=self.out,turn=110)
        self.assertEqual(self.r.cmd.call_count,1)
        self.assertTrue((self.out/'session-operations/load-ack-warning.json').exists())

    def test_native_lua_failure_is_not_ack_ambiguity(self):
        self.start();self.r.cmd.side_effect = NativeLuaFailure('bad native code')
        with self.assertRaises(NativeLuaFailure): self.s.issue_once('host','code','MainMenu')

    def test_cleanup_order_and_exact_callbacks(self):
        self.start();order=[]
        self.r.cmd.side_effect = self.exit_on_request
        def package():
            self.assertEqual(self.owner.poll(),0)
            order.append('package')
        self.s.close(before_menu=lambda:order.append('freeze-and-restore'),
                     restore_preferences=lambda:order.append('prefs'),
                     after_native_exit=lambda:order.append('observer-exit'),restore_package=package)
        self.assertEqual(order,['freeze-and-restore','prefs','observer-exit','package'])
        self.assertTrue(self.s.closed)
        self.assertTrue((self.out/'session-closed.json').exists())

    def test_freeze_failure_preserves_native_and_never_restores_package(self):
        self.start();package=Mock()
        def fail(): raise ValueError('freeze unconfirmed')
        with self.assertRaises(ValueError):
            self.s.close(before_menu=fail,restore_preferences=Mock(),restore_package=package)
        self.r.cmd.assert_not_called();package.assert_not_called()

    def test_preference_mismatch_never_issues_exit_or_restores(self):
        self.start();package=Mock()
        def fail(): raise ValueError('prefs differ')
        with self.assertRaises(ValueError): self.s.close(restore_preferences=fail,restore_package=package)
        self.r.cmd.assert_not_called();package.assert_not_called()

    def test_ambiguous_exit_with_actual_exit_is_not_retried(self):
        self.start()
        def once(*args,**kw):
            self.owner.code=0
            raise MissingAcknowledgment('exit','partial')
        self.r.cmd.side_effect=once
        self.s.close(restore_preferences=lambda:None)
        self.assertEqual(self.r.cmd.call_count,1)
        self.assertTrue(self.s.closed)

    def test_surviving_native_blocks_package_restore(self):
        self.start();package=Mock()
        with self.assertRaises(SessionError):
            self.s.close(restore_preferences=lambda:None,restore_package=package,exit_timeout=1)
        package.assert_not_called()

    def test_observer_failure_blocks_package_restore(self):
        self.start();package=Mock();self.r.cmd.side_effect=self.exit_on_request
        def fail(): raise ValueError('daemon exit unconfirmed')
        with self.assertRaises(ValueError):
            self.s.close(restore_preferences=lambda:None,after_native_exit=fail,restore_package=package)
        package.assert_not_called()

    def test_foreign_successor_blocks_package_restore(self):
        self.start();package=Mock()
        def exit(*args,**kw): self.owner.code=0;self.rows=[{'pid':81}]
        self.r.cmd.side_effect=exit
        with self.assertRaises(SessionError): self.s.close(restore_preferences=lambda:None,restore_package=package)
        package.assert_not_called()

    def test_changed_package_callback_is_failure_not_success(self):
        self.start();self.r.cmd.side_effect=self.exit_on_request
        def fail(): raise ValueError('foreign edited file')
        with self.assertRaises(ValueError): self.s.close(restore_preferences=lambda:None,restore_package=fail)
        self.assertFalse((self.out/'session-closed.json').exists())

    def test_nonzero_exit_restores_safely_but_does_not_pass(self):
        self.start();package=Mock()
        def exit(*args,**kw): self.owner.code=7
        self.r.cmd.side_effect=exit
        with self.assertRaises(SessionError): self.s.close(restore_preferences=lambda:None,restore_package=package)
        package.assert_called_once()
        self.assertFalse(json.loads((self.out/'session-closed.json').read_text())['verified'])

    def test_probe_import_and_construction_make_no_connections(self):
        r=make_probe_controller(self.out)
        self.assertEqual(r.last_interval_turn,1)
        self.assertEqual(r.seq,0)


if __name__ == '__main__': unittest.main()
