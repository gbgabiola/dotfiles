"""Validate restore behaviour using disposable snapshots and home directories."""

from contextlib import redirect_stderr, redirect_stdout
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import restore


class RestoreTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="restore-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "source"
        self.destination = self.root / "home with spaces"
        self.snapshot = self.root / "backup" / "sync-test"
        for directory in (self.source, self.destination, self.snapshot):
            directory.mkdir(parents=True)
        self.saved = self.snapshot / "config"
        self.target = self.destination / "config"
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()

    def run_restore(self):
        arguments = [
            "restore.py", str(self.snapshot),
            "--source", str(self.source),
            "--destination", str(self.destination),
        ]
        with mock.patch.object(sys, "argv", arguments):
            with redirect_stdout(self.stdout), redirect_stderr(self.stderr):
                restore.main()

    def managed_link(self):
        self.target.symlink_to(os.path.relpath(self.source / "config", self.destination))

    def test_restores_file_over_a_managed_link(self):
        self.saved.write_text("backup")
        self.managed_link()
        self.run_restore()
        self.assertFalse(self.target.is_symlink())
        self.assertEqual(self.target.read_text(), "backup")
        self.assertFalse(self.saved.exists())
        self.assertIn("Restored:", self.stdout.getvalue())
        self.assertEqual(list(self.snapshot.parent.iterdir()), [self.snapshot])

    def test_restores_directory_to_a_missing_destination(self):
        self.saved.mkdir()
        (self.saved / "nested").write_text("backup")
        self.run_restore()
        self.assertEqual((self.target / "nested").read_text(), "backup")
        self.assertFalse(self.saved.exists())

    def test_restores_a_dangling_backup_symlink(self):
        self.saved.symlink_to("missing")
        self.managed_link()
        self.run_restore()
        self.assertEqual(os.readlink(self.target), "missing")
        self.assertFalse(os.path.lexists(self.saved))

    def test_skips_an_unrelated_destination(self):
        self.saved.write_text("backup")
        self.target.write_text("user data")
        self.run_restore()
        self.assertEqual(self.target.read_text(), "user data")
        self.assertEqual(self.saved.read_text(), "backup")
        self.assertIn("Skipped unrelated entry", self.stderr.getvalue())

    def test_preserves_a_file_created_after_the_missing_target_check(self):
        self.saved.write_text("backup")
        lexists = os.path.lexists
        injected = False

        def create_after_check(path):
            nonlocal injected
            result = lexists(path)
            if Path(path) == self.target and not result and not injected:
                injected = True
                self.target.write_text("concurrent data")
            return result

        with mock.patch.object(restore.os.path, "lexists", side_effect=create_after_check):
            with self.assertRaises(FileExistsError):
                self.run_restore()
        self.assertTrue(injected)
        self.assertEqual(self.target.read_text(), "concurrent data")
        self.assertEqual(self.saved.read_text(), "backup")

    def test_preserves_a_destination_created_while_the_link_is_staged(self):
        for kind in ("file", "directory", "symlink"):
            with self.subTest(kind=kind):
                self.saved.write_text("backup")
                self.managed_link()
                previous_link = os.readlink(self.target)
                move = restore.move_without_overwrite

                def create_before_restore(source, destination):
                    if source == self.saved:
                        if kind == "file":
                            self.target.write_text("concurrent data")
                        elif kind == "directory":
                            self.target.mkdir()
                            (self.target / "data").write_text("concurrent data")
                        else:
                            self.target.symlink_to("concurrent-link")
                    move(source, destination)

                with mock.patch.object(
                    restore, "move_without_overwrite", side_effect=create_before_restore
                ):
                    with self.assertRaises(FileExistsError):
                        self.run_restore()
                self.assertEqual(self.saved.read_text(), "backup")
                recovery, = self.snapshot.parent.glob("restore-*")
                held = recovery / "config"
                self.assertEqual(os.readlink(held), previous_link)
                self.assertIn(str(held), self.stderr.getvalue())
                if kind == "directory":
                    self.assertEqual((self.target / "data").read_text(), "concurrent data")
                    (self.target / "data").unlink()
                    self.target.rmdir()
                elif kind == "symlink":
                    self.assertEqual(os.readlink(self.target), "concurrent-link")
                    self.target.unlink()
                else:
                    self.assertEqual(self.target.read_text(), "concurrent data")
                    self.target.unlink()
                held.unlink()
                recovery.rmdir()

    def test_preserves_a_file_that_replaced_the_link_before_staging(self):
        self.saved.write_text("backup")
        self.managed_link()
        move = restore.move_without_overwrite

        def replace_before_staging(source, destination):
            if source == self.target:
                self.target.unlink()
                self.target.write_text("concurrent data")
            move(source, destination)

        with mock.patch.object(
            restore, "move_without_overwrite", side_effect=replace_before_staging
        ):
            with self.assertRaises(FileExistsError):
                self.run_restore()
        self.assertEqual(self.target.read_text(), "concurrent data")
        self.assertEqual(self.saved.read_text(), "backup")
        self.assertEqual(list(self.snapshot.parent.iterdir()), [self.snapshot])

    def test_restores_the_managed_link_after_a_failed_move(self):
        self.saved.write_text("backup")
        self.managed_link()
        previous_link = os.readlink(self.target)
        move = restore.move_without_overwrite

        def fail_restore(source, destination):
            if source == self.saved:
                raise PermissionError("injected failure")
            move(source, destination)

        with mock.patch.object(
            restore, "move_without_overwrite", side_effect=fail_restore
        ):
            with self.assertRaises(PermissionError):
                self.run_restore()
        self.assertEqual(self.saved.read_text(), "backup")
        self.assertEqual(os.readlink(self.target), previous_link)
        self.assertEqual(list(self.snapshot.parent.iterdir()), [self.snapshot])

    def test_keeps_recovery_data_when_the_process_is_interrupted(self):
        self.saved.write_text("backup")
        self.managed_link()
        previous_link = os.readlink(self.target)
        move = restore.move_without_overwrite

        def interrupt_restore(source, destination):
            if source == self.saved:
                raise KeyboardInterrupt
            move(source, destination)

        with mock.patch.object(
            restore, "move_without_overwrite", side_effect=interrupt_restore
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_restore()
        recovery, = self.snapshot.parent.glob("restore-*")
        self.assertEqual(os.readlink(recovery / "config"), previous_link)
        self.assertEqual(self.saved.read_text(), "backup")
        self.assertFalse(os.path.lexists(self.target))
        self.assertIn(str(recovery / "config"), self.stdout.getvalue())
        self.run_restore()
        self.assertEqual(self.target.read_text(), "backup")

    def test_missing_atomic_operation_preserves_the_link_and_snapshot(self):
        self.saved.write_text("backup")
        self.managed_link()
        previous_link = os.readlink(self.target)
        with mock.patch.object(restore.ctypes, "CDLL", return_value=object()):
            with self.assertRaises(OSError):
                self.run_restore()
        self.assertEqual(self.saved.read_text(), "backup")
        self.assertEqual(os.readlink(self.target), previous_link)
        self.assertEqual(list(self.snapshot.parent.iterdir()), [self.snapshot])

    def test_atomic_move_never_replaces_existing_entries(self):
        self.saved.write_text("backup")
        for kind in ("file", "directory", "symlink"):
            with self.subTest(kind=kind):
                if kind == "file":
                    self.target.write_text("user data")
                elif kind == "directory":
                    self.target.mkdir()
                else:
                    self.target.symlink_to("missing")
                with self.assertRaises(FileExistsError):
                    restore.move_without_overwrite(self.saved, self.target)
                self.assertEqual(self.saved.read_text(), "backup")
                if kind == "file":
                    self.assertEqual(self.target.read_text(), "user data")
                    self.target.unlink()
                elif kind == "directory":
                    self.assertTrue(self.target.is_dir())
                    self.target.rmdir()
                else:
                    self.assertEqual(os.readlink(self.target), "missing")
                    self.target.unlink()

    def test_repeat_restore_is_a_noop_after_success(self):
        self.saved.write_text("backup")
        self.managed_link()
        self.run_restore()
        self.run_restore()
        self.assertEqual(self.target.read_text(), "backup")
        self.assertEqual(list(self.snapshot.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
