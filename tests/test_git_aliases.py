"""Exercise the tracked Git aliases in disposable repositories."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
GIT = shutil.which("git")


@unittest.skipUnless(GIT, "Git is required for alias regression tests")
class GitAliasTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="git-alias-")
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        self.repository = directory / "repository with spaces"
        self.repository.mkdir()
        home = directory / "home"
        home.mkdir()
        self.environment = {
            key: value for key, value in os.environ.items()
            if not key.startswith("GIT_")
        }
        self.environment.update(
            HOME=str(home),
            GIT_CONFIG_NOSYSTEM="1",
            GIT_CONFIG_GLOBAL=str(ROOT / "home/.gitconfig"),
        )
        self.git("init", "-q")

    def git(self, *arguments):
        return subprocess.run(
            [GIT, *arguments],
            cwd=self.repository,
            env=self.environment,
            text=True,
            capture_output=True,
            timeout=10,
        )

    def test_ignore_treats_arguments_as_literal_patterns(self):
        patterns = (
            "*.log",
            "touch marker",
            "$(touch marker)",
            "`touch marker`",
            "semi; touch marker",
            "single'quote",
            'double"quote',
            "directory with spaces/",
            "-n",
            "#comment",
            "!keep.log",
            r"literal\backslash",
        )
        result = self.git("ignore", *patterns)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(
            (self.repository / ".gitignore").read_text(),
            "".join(pattern + "\n" for pattern in patterns),
        )
        self.assertEqual(
            {entry.name for entry in self.repository.iterdir()},
            {".git", ".gitignore"},
        )

    def test_ignore_does_not_execute_the_second_argument(self):
        result = self.git("ignore", "safe-pattern", "touch marker")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.repository / "marker").exists())
        self.assertEqual(
            (self.repository / ".gitignore").read_text(),
            "safe-pattern\ntouch marker\n",
        )

    def test_ignore_appends_without_replacing_existing_rules(self):
        ignore_file = self.repository / ".gitignore"
        ignore_file.write_text("existing-rule\n")
        for pattern in ("*.log", "directory with spaces/"):
            result = self.git("ignore", pattern)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            ignore_file.read_text(),
            "existing-rule\n*.log\ndirectory with spaces/\n",
        )

    def test_ignore_requires_a_pattern(self):
        result = self.git("ignore")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage: git ignore", result.stderr)
        self.assertFalse((self.repository / ".gitignore").exists())

    def test_stat_handles_unusual_tracked_filenames(self):
        filenames = (
            "file with spaces",
            "tab\tname",
            "line\nbreak",
            "-leading-option",
            "semi; touch marker",
            "single'quote",
        )
        for filename in filenames:
            (self.repository / filename).write_text("one\ntwo\n")
        result = self.git("add", "--", *filenames)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.git("stat")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout.splitlines()[-1].split(), ["12", "total"])
        self.assertFalse((self.repository / "marker").exists())

    def test_stat_handles_an_empty_repository(self):
        result = self.git("stat")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout.strip(), "0")

    def test_stat_handles_a_single_tracked_file(self):
        (self.repository / "ordinary.txt").write_text("one\ntwo\nthree\n")
        result = self.git("add", "ordinary.txt")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.git("stat")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.split(), ["3", "ordinary.txt"])


if __name__ == "__main__":
    unittest.main()
