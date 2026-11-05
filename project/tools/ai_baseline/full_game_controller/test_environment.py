"""Offline content-selection checks; no native connection or preference writes."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from . import environment


class ContentSelection(unittest.TestCase):
    def test_isolated_copy_is_the_only_allowed_csc(self):
        selected = 'd0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a08'
        original = dict(mods={environment.CSC: True}, entries=[], auto_start=False)
        absent = dict(mods={environment.CSC: False, selected: False})
        ready = dict(mods={environment.CSC: False, selected: True})
        controller = Mock()
        with tempfile.TemporaryDirectory() as directory, patch.object(
                environment, 'flags', side_effect=[original, absent, ready]):
            output = Path(directory)
            environment.configure(controller, output, csc_id=selected)
            backup = environment.read(output / 'original-preferences.json')
            self.assertEqual(backup, original)
            self.assertEqual(environment.read(output / 'native-menu-configuration.json')
                             ['enabled_mod_ids'], [selected])
        commands = [call.args[0] for call in controller.cmd.call_args_list]
        self.assertIn("m.Id~='" + selected + "'", commands[0])
        self.assertIn("m.Id=='" + selected + "'", commands[1])

    def test_invalid_identity_is_rejected_before_native_io(self):
        controller = Mock()
        with patch.object(environment, 'flags') as flags:
            with self.assertRaises(ValueError):
                environment.configure(controller, Path('unused'), csc_id="';error('bad')")
        flags.assert_not_called()
        controller.cmd.assert_not_called()

    def test_an_extra_enabled_mod_is_not_silently_accepted(self):
        controller = Mock()
        selected = dict(mods={environment.CSC: True, 'unexpected': True}, entries=[])
        with tempfile.TemporaryDirectory() as directory, patch.object(
                environment, 'flags', side_effect=[selected, selected, selected]):
            with self.assertRaisesRegex(RuntimeError, 'CSC-only'):
                environment.configure(controller, Path(directory))
