"""Real probe/read command integration for classified pretransmission discovery."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

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


if __name__=='__main__':unittest.main()
