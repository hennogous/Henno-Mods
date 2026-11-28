"""Real probe/read command integration for classified pretransmission discovery."""
import json
import itertools
from pathlib import Path
import tempfile
from types import MethodType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from . import controller as control
from . import probe
from .transport import MissingAcknowledgment, NativeLuaFailure


class StateDiscoveryRetryTests(unittest.TestCase):
    scratch = None

    def setUp(self):
        parent=Path(self.scratch or tempfile.gettempdir()).resolve()
        self.temp=tempfile.TemporaryDirectory(prefix='csc-discovery-',dir=parent)
        self.root=Path(self.temp.name).resolve()
        assert self.root.parent==parent, 'Temporary cleanup target escaped parent'
        self.addCleanup(self.temp.cleanup)
        self.user=self.root/'user';self.user.mkdir()
        self.output=self.root/'output';self.sent=[];self.discovered=[]
        self.addCleanup(patch.stopall)
        patch.object(control.time,'sleep',lambda seconds:None).start()

    def runner(self, discovery, response=None):
        def discover(required):
            self.discovered.append(required)
            return discovery(len(self.discovered))
        with patch.object(probe,'discover_contexts',discover):
            runner=probe.make_probe_controller(self.output,user_root=self.user)
        def receive(code,*args,**kwargs):
            self.sent.append(code)
            if response is not None: raise response
            return 'CSC_SHARED_STATE 131 false 0 0 true true',True
        patch.object(control,'receive_command',receive).start()
        return runner

    def test_real_probe_readonly_discovery_recovers_then_transmits_query_once(self):
        def discovery(attempt):
            if attempt<=3: raise RuntimeError('No responsive tuner states')
            return 4318,{'GameCore_Tuner':1}
        runner=self.runner(discovery)
        proof=runner.state_read('closed-source')
        self.assertEqual(proof['turn'],131);self.assertFalse(proof['active'])
        self.assertEqual(len(self.discovered),4);self.assertEqual(self.sent,[control.HANDOFF])
        self.assertEqual(runner.seq,2)
        journal=[json.loads(row)for row in (self.output/'controller-journal.ndjson').read_text().splitlines()]
        self.assertEqual(sum(row['event']=='readonly-state-query-retry'for row in journal),1)

    def test_persistent_unavailable_is_bounded_to_three_read_attempts_no_lua_send(self):
        def unavailable(attempt): raise RuntimeError('No responsive tuner states')
        runner=self.runner(unavailable)
        with self.assertRaises(control.StateDiscoveryUnavailable): runner.state_read('unavailable')
        self.assertEqual(runner.seq,3);self.assertEqual(len(self.discovered),9)
        self.assertEqual(self.sent,[])

    def test_unknown_discovery_runtime_error_is_not_reclassified_or_retried(self):
        def unexpected(attempt): raise RuntimeError('Unexpected discovery parser failure')
        runner=self.runner(unexpected)
        with self.assertRaisesRegex(RuntimeError,'Unexpected discovery parser failure'):
            runner.state_read('unknown')
        self.assertEqual(len(self.discovered),1);self.assertEqual(runner.seq,1);self.assertEqual(self.sent,[])

    def test_native_lua_failure_remains_one_transmission_no_state_read_retry(self):
        runner=self.runner(lambda attempt:(4318,{'GameCore_Tuner':1}),NativeLuaFailure('No responsive tuner states'))
        with self.assertRaises(NativeLuaFailure): runner.state_read('native-error')
        self.assertEqual(self.sent,[control.HANDOFF]);self.assertEqual(len(self.discovered),1)

    def test_direct_mutation_command_does_not_gain_outer_discovery_retry(self):
        def unavailable(attempt): raise RuntimeError('No responsive tuner states')
        runner=self.runner(unavailable)
        with self.assertRaises(control.StateDiscoveryUnavailable):
            runner.cmd('AutoplayManager.SetActive(true);','GameCore_Tuner','mutation')
        self.assertEqual(runner.seq,1);self.assertEqual(len(self.discovered),3);self.assertEqual(self.sent,[])

    def test_ambiguous_mutation_transmission_is_never_replayed(self):
        failure=MissingAcknowledgment('mutation','ambiguous native reply')
        runner=self.runner(lambda attempt:(4318,{'GameCore_Tuner':1}),failure)
        with self.assertRaises(MissingAcknowledgment):
            runner.cmd('AutoplayManager.SetActive(true);','GameCore_Tuner','mutation')
        self.assertEqual(len(self.sent),1);self.assertEqual(len(self.discovered),1);self.assertEqual(runner.seq,1)


class AutoplayDiscoveryTests(unittest.TestCase):
    """Busy discovery may wait; transmitted control failures must still stop."""

    def runner(self, rows):
        runner=SimpleNamespace(root=Path(__file__).parent/'nonexistent-discovery-test-root',
            diagnostics=SimpleNamespace(journal=Mock(),write=Mock()),
            state_read=Mock(side_effect=rows),ready=Mock(),cmd=Mock(),
            boundary_decision=lambda turn,target,n:('done',n+1),
            continue_after_victory=lambda target,row:False,
            capture_blocker=Mock(),dismiss_observer_warning=Mock(),release_disaster=Mock())
        runner._metadata=MethodType(control.FullGameController._metadata,runner)
        return runner

    def await_target(self, runner):
        # Synthetic forty-second clock reaches the optional presentation check
        # without real sleeping or a game. Existing timeout bounds stay active.
        with patch.object(control.time,'sleep'),patch.object(control.time,'monotonic',side_effect=itertools.count(0,40)):
            control.FullGameController._await_target(runner,135)

    @staticmethod
    def done():return dict(turn=135,active=False,remaining=0,local_player=0,player0_human=True)

    def test_missing_activation_reply_uses_only_the_exact_existing_interval(self):
        active=dict(turn=132,active=True,remaining=3,local_player=-1,player0_human=False,player0_alive=True)
        complete=dict(self.done(),player0_alive=True)
        for evidence,accepted in ((active,True),(complete,True),(dict(active,remaining=4),False),
                                  (dict(active,local_player=0),False),(dict(complete,turn=134),False)):
            with self.subTest(evidence=evidence):
                runner=self.runner([evidence]);runner.last_interval_turn=130;runner._await_target=Mock()
                runner.cmd.side_effect=MissingAcknowledgment('sent-once','')
                if accepted:
                    control.FullGameController.play(runner,135)
                    runner._await_target.assert_called_once_with(135)
                else:
                    with self.assertRaises(MissingAcknowledgment):
                        control.FullGameController.play(runner,135)
                    runner._await_target.assert_not_called()
                runner.cmd.assert_called_once()
                runner.state_read.assert_called_once_with('verify-transmitted-autoplay-135')

    def test_busy_progress_discovery_returns_to_reading_without_activation(self):
        runner=self.runner([control.StateDiscoveryUnavailable('busy'),self.done()])
        self.await_target(runner)
        runner.cmd.assert_not_called();runner.ready.assert_called_once_with(135,'after-135')
        runner.diagnostics.journal.assert_called_once_with('autoplay-readonly-discovery-deferred',
            target=135,phase='progress',no_control_replayed=True)

    def test_busy_optional_popup_discovery_recovers_with_fresh_progress(self):
        active=dict(turn=130,active=True,remaining=5,local_player=-1,player0_human=False)
        runner=self.runner([active,self.done()])
        runner.release_disaster.side_effect=control.StateDiscoveryUnavailable('busy')
        self.await_target(runner)
        runner.release_disaster.assert_called_once_with(135);runner.cmd.assert_not_called()
        runner.ready.assert_called_once_with(135,'after-135')
        runner.diagnostics.journal.assert_called_once_with('autoplay-readonly-discovery-deferred',
            target=135,phase='presentation',no_control_replayed=True)

    def test_persistent_unavailable_keeps_ten_minute_progress_bound(self):
        runner=self.runner(itertools.repeat(control.StateDiscoveryUnavailable('busy')))
        with self.assertRaisesRegex(RuntimeError,'No confirmed progress for ten minutes'):self.await_target(runner)
        runner.cmd.assert_not_called();runner.ready.assert_not_called()

    def test_acknowledged_close_before_next_discovery_failure_is_not_replayed(self):
        active=dict(turn=130,active=True,remaining=5,local_player=-1,player0_human=False)
        runner=self.runner([active,self.done()])
        # Model the actual wrapper order: an earlier guard closes its popup,
        # then the next guard's read-only context inventory becomes unavailable.
        runner.dismiss_observer_warning.side_effect=lambda target:runner.cmd('Close();','WonderBuiltPopup','acknowledged-close')
        runner.release_disaster.side_effect=control.StateDiscoveryUnavailable('busy')
        self.await_target(runner)
        runner.cmd.assert_called_once_with('Close();','WonderBuiltPopup','acknowledged-close')
        runner.ready.assert_called_once_with(135,'after-135')

    def test_ambiguous_popup_send_is_fatal_without_replay(self):
        active=dict(turn=130,active=True,remaining=5,local_player=-1,player0_human=False)
        for failure in (MissingAcknowledgment('popup','ambiguous'),NativeLuaFailure('native failure')):
            with self.subTest(failure=type(failure).__name__):
                runner=self.runner([active]);runner.release_disaster.side_effect=failure
                with self.assertRaises(type(failure)):self.await_target(runner)
                runner.release_disaster.assert_called_once();runner.ready.assert_not_called()
                runner.cmd.assert_not_called();runner.diagnostics.journal.assert_not_called()


if __name__=='__main__':unittest.main()
