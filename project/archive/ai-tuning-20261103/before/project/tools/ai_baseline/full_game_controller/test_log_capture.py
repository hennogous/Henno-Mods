import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from full_game_controller.log_capture import (
    LogGenerationChanged, capture_log_baseline, read_log_delta)


class LogCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'AI_CityBuild.csv'

    def test_missing_pre_ai_file_then_first_real_observation(self):
        start = capture_log_baseline(self.path)
        self.assertFalse(start.existed)
        self.assertEqual(start.evidence()['offset'], 0)
        self.assertIsNone(start.evidence()['prefix_sha256'])
        self.path.write_bytes(b'turn,city\n110,Kobdo\n')
        boundary, delta = read_log_delta(self.path, start)
        self.assertTrue(boundary.existed)
        self.assertEqual(delta, b'turn,city\n110,Kobdo\n')

    def test_missing_post_ai_file_is_not_an_empty_observation(self):
        start = capture_log_baseline(self.path)
        with self.assertRaises(FileNotFoundError):
            read_log_delta(self.path, start)

    def test_existing_empty_file_is_distinct_from_missing(self):
        missing = capture_log_baseline(self.path)
        self.path.touch()
        empty = capture_log_baseline(self.path)
        self.assertFalse(missing.existed)
        self.assertTrue(empty.existed)
        self.assertIsNotNone(empty.evidence()['prefix_sha256'])

    def test_only_same_generation_appends_are_accepted(self):
        self.path.write_bytes(b'header\n110,a\n')
        start = capture_log_baseline(self.path)
        self.path.write_bytes(start.data + b'111,b\n')
        after, delta = read_log_delta(self.path, start)
        self.assertEqual(delta, b'111,b\n')
        for changed in (b'header\n', b'new generation\n'):
            self.path.write_bytes(changed)
            with self.assertRaises(LogGenerationChanged):
                read_log_delta(self.path, after)

    def test_wrong_path_or_missing_directory_is_not_fresh_logging(self):
        start = capture_log_baseline(self.path)
        with self.assertRaises(ValueError):
            read_log_delta(self.path.with_name('AI_Construction.csv'), start)
        with self.assertRaises(FileNotFoundError):
            capture_log_baseline(self.path.parent / 'wrong-root' / self.path.name)

    def test_access_failures_are_not_hidden_as_missing_logs(self):
        with patch.object(Path, 'read_bytes', side_effect=PermissionError('locked')):
            with self.assertRaises(PermissionError):
                capture_log_baseline(self.path)


if __name__ == '__main__':
    unittest.main()
