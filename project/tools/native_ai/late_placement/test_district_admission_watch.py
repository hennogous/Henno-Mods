"""Guard optional diagnostics without attaching to or launching a game."""
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from district_admission_watch import AdmissionWatch, specification, validate_options


class AdmissionGuards(unittest.TestCase):
    def test_dependencies_are_an_explicit_paired_opt_in(self):
        validate_options(False, None, None)
        validate_options(True, Path('existing-deps'), Path('qualified-dll'))
        for enabled, deps, binary in [(True, None, None), (True, Path('deps'), None),
                                      (True, None, Path('dll')), (False, Path('deps'), Path('dll')),
                                      (False, Path('deps'), None), (False, None, Path('dll'))]:
            with self.subTest(enabled=enabled, deps=deps, binary=binary):
                with self.assertRaisesRegex(ValueError, 'requires both'):
                    validate_options(enabled, deps, binary)

    def test_unqualified_binary_is_rejected_before_pe_addresses_are_read(self):
        # An existing text file needs no temporary write on restricted hosts.
        with self.assertRaisesRegex(ValueError, 'artifact identity'):
            specification(Path(__file__))

    def test_module_identity_mismatch_never_attaches(self):
        watch=AdmissionWatch.__new__(AdmissionWatch)
        watch.attached=None;watch.frida=Mock();watch.spec=dict(path='C:/qualified.dll')
        owner=Mock();owner.poll.return_value=None
        with self.assertRaisesRegex(ValueError, 'Loaded module proof'):
            watch.attach(owner, {})
        watch.frida.attach.assert_not_called()

    def test_live_owner_is_never_detached_during_cleanup(self):
        watch=AdmissionWatch.__new__(AdmissionWatch)
        watch.owner=Mock();watch.owner.poll.return_value=None
        watch.attached=Mock();watch.write=Mock()
        with self.assertRaisesRegex(RuntimeError, 'live owner'):
            watch.after_exit()
        watch.attached.detach.assert_not_called()
        watch.write.assert_not_called()

    def test_freeze_waits_for_pairing_and_then_is_idempotent(self):
        watch=AdmissionWatch.__new__(AdmissionWatch)
        watch.output=Path('diagnostic-output');watch.write=Mock();watch.frozen=None
        rpc=Mock();rpc.freeze.side_effect=[dict(frozen=False,active=1),dict(frozen=True,active=0)]
        watch.script=SimpleNamespace(exports_sync=rpc)
        with patch('district_admission_watch.time.sleep'):
            watch.freeze();watch.freeze()
        self.assertEqual(rpc.freeze.call_count,2)
        self.assertEqual(watch.frozen,dict(frozen=True,active=0))

    def test_faulted_or_incomplete_measurement_is_not_qualified(self):
        watch=AdmissionWatch.__new__(AdmissionWatch)
        clean=dict(frozen=True,active=0,stopReason=None,faults=[])
        watch.frozen=clean;watch.messages=[];watch.qualify()
        for changed in [dict(frozen=False),dict(active=1),dict(stopReason='record_bound'),
                        dict(faults=['read failure'])]:
            with self.subTest(changed=changed):
                watch.frozen=dict(clean,**changed)
                with self.assertRaisesRegex(RuntimeError,'measurement'):
                    watch.qualify()
        watch.frozen=clean;watch.messages=[{'type':'error'}]
        with self.assertRaisesRegex(RuntimeError,'measurement'):
            watch.qualify()


if __name__=='__main__':unittest.main()
