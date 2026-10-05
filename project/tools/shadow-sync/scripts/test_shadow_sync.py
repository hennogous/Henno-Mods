#!/usr/bin/env python3
"""Exercise real Git divergence, dirty worktrees, conflicts and fail-fast behavior."""

import argparse
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True

from shadow_sync import main, synchronize
from git_worker import SyncError, git, operate


SCRATCH = None


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="git-test-", dir=SCRATCH)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.origin = self.root / "origin.git"
        self.mac = self.root / "Mac with spaces"
        self.shadow = self.root / "Shadow with spaces"
        self.run_git("init", "--bare", "--initial-branch=main", str(self.origin))
        self.run_git("clone", str(self.origin), str(self.mac))
        self.identity(self.mac)
        (self.mac / "shared.txt").write_text("base\n")
        (self.mac / "delete-me.txt").write_text("delete later\n")
        (self.mac / ".gitignore").write_text("ignored/\n")
        git(self.mac, "add", ".")
        git(self.mac, "commit", "-m", "base")
        git(self.mac, "push", "-u", "origin", "main")
        self.run_git("clone", str(self.origin), str(self.shadow))
        self.identity(self.shadow)
        # Local bare transports have no GitHub identity; only this fixture uses None.
        self.spec = {"name": "fixture", "github": None, "branch": "main",
                     "mac": str(self.mac), "shadow": str(self.shadow)}
        self.base = git(self.mac, "rev-parse", "HEAD")

    def run_git(self, *args):
        subprocess.run(["git", *args], check=True, capture_output=True)

    def identity(self, path):
        git(path, "config", "user.name", "Sync Test")
        git(path, "config", "user.email", "sync-test@example.invalid")

    def sync(self, preview=False, specs=None, shadow_git=False):
        def call(**request):
            self.assertFalse(not shadow_git and request["host"] == "shadow" and request["action"] in ("publish", "finish"),
                             "Shadow must not need GitHub authentication")
            return operate(**request)
        def transfer(spec, base, expected_head):
            bundle = self.root / "shadow.bundle"
            git(spec["shadow"], "bundle", "create", str(bundle), f"{base}..HEAD")
            return bundle
        def deliver(spec, incoming, state):
            if incoming != state["head"]:
                base = git(spec["mac"], "merge-base", incoming, state["origin_head"])
                if base != incoming:
                    bundle = self.root / "to-shadow.bundle"
                    git(spec["mac"], "bundle", "create", str(bundle), f"{base}..{incoming}", "HEAD")
                    git(spec["shadow"], "bundle", "verify", str(bundle))
                    git(spec["shadow"], "fetch", "--no-tags", str(bundle), "HEAD")
                    self.assertEqual(git(spec["shadow"], "rev-parse", "FETCH_HEAD"), incoming)
            return operate(spec, "shadow", "merge-known", incoming=incoming, expected=state)
        with contextlib.redirect_stdout(io.StringIO()):
            return synchronize(specs or [self.spec], call, "test checkpoint", preview,
                               transfer, deliver, shadow_git=shadow_git)

    def assert_converged(self):
        heads = {git(p, "rev-parse", "HEAD") for p in (self.mac, self.shadow)}
        heads.add(git(self.origin, "rev-parse", "main"))
        self.assertEqual(len(heads), 1)
        for p in (self.mac, self.shadow):
            self.assertEqual(git(p, "status", "--porcelain"), "")

    def test_dirty_both_hosts_plus_remote_changes(self):
        third = self.root / "third"
        self.run_git("clone", str(self.origin), str(third))
        self.identity(third)
        (third / "github.txt").write_text("from GitHub\n")
        git(third, "add", ".")
        git(third, "commit", "-m", "third writer")
        git(third, "push")
        (self.mac / "Mac source.txt").write_text("Mac work\n")
        (self.shadow / "Shadow source.txt").write_text("Shadow work\n")
        self.sync()
        self.assert_converged()
        for p in (self.mac, self.shadow):
            self.assertEqual((p / "Mac source.txt").read_text(), "Mac work\n")
            self.assertEqual((p / "Shadow source.txt").read_text(), "Shadow work\n")
            self.assertTrue((p / "github.txt").is_file())

    def test_clean_run_and_repeat_create_no_commits(self):
        self.sync()
        self.sync()
        self.assert_converged()
        self.assertEqual(git(self.mac, "rev-parse", "HEAD"), self.base)

    def test_preview_does_not_save_or_push(self):
        (self.mac / "pending.txt").write_text("pending\n")
        self.sync(preview=True)
        self.assertEqual(git(self.mac, "rev-parse", "HEAD"), self.base)
        self.assertEqual(git(self.origin, "rev-parse", "main"), self.base)
        self.assertIn("pending.txt", git(self.mac, "status", "--porcelain"))

    def test_staged_unstaged_deleted_and_ignored_files(self):
        (self.mac / "staged.txt").write_text("staged\n")
        git(self.mac, "add", "staged.txt")
        (self.mac / "staged.txt").write_text("latest saved contents\n")
        (self.mac / "delete-me.txt").unlink()
        (self.mac / "ignored").mkdir()
        (self.mac / "ignored/output.txt").write_text("not source\n")
        self.sync()
        self.assert_converged()
        self.assertEqual((self.shadow / "staged.txt").read_text(), "latest saved contents\n")
        self.assertFalse((self.shadow / "delete-me.txt").exists())
        self.assertFalse((self.shadow / "ignored").exists())
        self.assertTrue((self.mac / "ignored/output.txt").exists())

    def test_conflict_preserves_both_checkpoint_commits(self):
        (self.mac / "shared.txt").write_text("Mac edit\n")
        (self.shadow / "shared.txt").write_text("Shadow edit\n")
        with self.assertRaises(SyncError):
            self.sync()
        self.assertEqual(git(self.mac, "show", "HEAD:shared.txt"), "Mac edit")
        self.assertEqual(git(self.shadow, "show", "HEAD:shared.txt"), "Shadow edit")
        self.assertTrue(git(self.shadow, "ls-files", "--unmerged"))
        self.assertEqual(git(self.origin, "rev-parse", "main"), git(self.mac, "rev-parse", "HEAD"))

    def test_all_checkouts_preflight_before_committing(self):
        (self.mac / "pending.txt").write_text("pending\n")
        git(self.shadow, "switch", "-c", "wrong-branch")
        with self.assertRaises(SyncError):
            self.sync()
        self.assertEqual(git(self.mac, "rev-parse", "HEAD"), self.base)
        self.assertEqual(git(self.mac, "diff", "--cached", "--name-only"), "")

    def test_expected_remote_and_snapshot_are_enforced(self):
        bad = dict(self.spec, github="hennogous/expected")
        with self.assertRaises(SyncError):
            operate(bad, "mac", "inspect")
        state = operate(self.spec, "mac", "inspect")
        (self.mac / "late.txt").write_text("late\n")
        with self.assertRaises(SyncError):
            operate(self.spec, "mac", "checkpoint", message="test", expected=state)
        self.assertEqual(git(self.mac, "rev-parse", "HEAD"), self.base)

    def test_master_branch_is_supported(self):
        for p in (self.mac, self.shadow):
            git(p, "branch", "-m", "master")
            git(p, "push", "-u", "origin", "master")
        self.spec["branch"] = "master"
        (self.shadow / "master.txt").write_text("master source\n")
        self.sync()
        self.assertEqual(git(self.mac, "rev-parse", "HEAD"), git(self.shadow, "rev-parse", "HEAD"))
        self.assertEqual(git(self.origin, "rev-parse", "master"), git(self.mac, "rev-parse", "HEAD"))

    def test_direct_git_mode_when_shadow_has_credentials(self):
        (self.mac / "mac.txt").write_text("Mac work\n")
        (self.shadow / "shadow.txt").write_text("Shadow work\n")
        self.sync(shadow_git=True)
        self.assert_converged()
        self.assertEqual((self.mac / "shadow.txt").read_text(), "Shadow work\n")
        self.assertEqual((self.shadow / "mac.txt").read_text(), "Mac work\n")

    def test_cli_default_syncs_directly_without_bundles(self):
        (self.mac / "mac-default.txt").write_text("Mac work\n")
        (self.shadow / "shadow-default.txt").write_text("Shadow work\n")
        def local_remote(request, target):
            return operate(**request)
        with patch("shadow_sync.bindings", return_value=[self.spec]), \
             patch("shadow_sync.remote", side_effect=local_remote), \
             patch("shadow_sync.deliver_bundle", side_effect=AssertionError("Default must use direct Git")), \
             patch("shadow_sync.receive_bundle", side_effect=AssertionError("Default must use direct Git")), \
             patch.object(sys, "argv", ["shadow-sync"]), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(), 0)
        self.assert_converged()
        self.assertEqual((self.mac / "shadow-default.txt").read_text(), "Shadow work\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch", required=True, help="output folder for isolated test repositories")
    args, extra = parser.parse_known_args()
    SCRATCH = Path(args.scratch).resolve()
    SCRATCH.mkdir(parents=True, exist_ok=True)
    unittest.main(argv=[__file__, *extra])
