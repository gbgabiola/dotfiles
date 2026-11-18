"""Integration checks using isolated homes and local Git repositories."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipIf(os.geteuid() == 0, "Installer requires a regular user")
class InstallUpdateTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="dotfiles integration ")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.home = self.directory / "home"
        self.home.mkdir()
        self.environment = dict(os.environ, HOME=str(self.home))
        self.checkout = self.directory / "checkout with spaces"
        shutil.copytree(ROOT, self.checkout, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        subprocess.run(["git", "init", "-q", str(self.checkout)], check=True)

    def run_install(self, *arguments):
        return subprocess.run(
            ["bash", str(self.checkout / "install.sh"), *arguments],
            cwd=self.directory, env=self.environment,
            capture_output=True, text=True, timeout=10,
        )

    def test_dry_run_does_not_write_to_home(self):
        result = self.run_install("--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(list(self.home.iterdir()), [])
        self.assertFalse((self.checkout / "backup").exists())

    def test_install_is_repeatable_and_excludes_local_templates(self):
        for _ in range(2):
            result = self.run_install()
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (self.home / ".zshrc").resolve(),
            self.checkout / "home/.zshrc",
        )
        self.assertFalse((self.home / ".localrc").exists())
        self.assertFalse((self.home / ".localrc.example").exists())
        self.assertFalse((self.checkout / "backup").exists())

    def test_noninteractive_install_preserves_conflicts(self):
        target = self.home / ".zshrc"
        target.write_text("personal configuration")
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(target.read_text(), "personal configuration")
        self.assertIn("Skipped:", result.stderr)
        self.assertFalse((self.checkout / "backup").exists())

    @unittest.skipUnless(shutil.which("zsh"), "Zsh is required")
    def test_updater_rejects_dirty_checkout_before_fetching(self):
        result = subprocess.run(
            ["zsh", str(self.checkout / "scripts/update.zsh")],
            cwd=self.directory, env=self.environment,
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("local changes", result.stderr)
        self.assertEqual(list(self.home.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
