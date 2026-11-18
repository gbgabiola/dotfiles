"""Check sync path boundaries through its command-line entry point."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SyncPathTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="sync paths ")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "config").write_text("shared configuration")
        self.backup = self.root / "backup"

    def run_sync(self, destination, *options):
        return subprocess.run(
            [sys.executable, "-B", str(ROOT / "sync.py"), str(self.source),
             str(destination), str(self.backup), *options],
            capture_output=True, text=True, timeout=10,
        )

    def assert_rejected(self, destination, *options):
        before = set(self.source.rglob("*"))
        result = self.run_sync(destination, *options)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(set(self.source.rglob("*")), before)
        self.assertFalse(self.backup.exists())
        self.assertEqual((self.source / "config").read_text(), "shared configuration")

    def test_rejects_identical_source_and_destination(self):
        self.assert_rejected(self.source)

    def test_rejects_nested_destination(self):
        destination = self.source / "nested"
        destination.mkdir()
        self.assert_rejected(destination)

    def test_rejects_nested_destination_during_dry_run(self):
        destination = self.source / "nested"
        destination.mkdir()
        self.assert_rejected(destination, "--dry-run")

    def test_rejects_symlink_to_nested_destination(self):
        destination = self.source / "nested"
        destination.mkdir()
        alias = self.root / "destination-alias"
        alias.symlink_to(destination)
        self.assert_rejected(alias)

    def test_allows_a_sibling_destination(self):
        destination = self.root / "destination"
        destination.mkdir()
        result = self.run_sync(destination)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((destination / "config").resolve(), self.source / "config")

    def test_allows_source_beneath_destination_home(self):
        result = self.run_sync(self.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / "config").resolve(), self.source / "config")


if __name__ == "__main__":
    unittest.main()
