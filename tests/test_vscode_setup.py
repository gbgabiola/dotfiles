"""Verify extension setup without installing actual extensions."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("zsh"), "Zsh is required")
class VSCodeSetupTests(unittest.TestCase):
    def run_setup(self, answers, fail=False):
        temporary = tempfile.TemporaryDirectory(prefix="vscode-setup-")
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        binary = directory / "bin"
        binary.mkdir()
        code = binary / "code"
        code.write_text(
            '#!/bin/sh\nprintf "%s\\n" "$*" >> "$CALL_LOG"\n'
            'if [ "$FAIL_CODE" = 1 ]; then exit 7; fi\n'
        )
        code.chmod(0o755)
        sleep = binary / "sleep"
        sleep.write_text('#!/bin/sh\nprintf "sleep\\n" >> "$CALL_LOG"\n')
        sleep.chmod(0o755)
        log = directory / "calls"
        environment = dict(
            os.environ, PATH=str(binary) + os.pathsep + os.environ["PATH"],
            CALL_LOG=str(log), FAIL_CODE="1" if fail else "0",
        )
        result = subprocess.run(
            ["zsh", str(ROOT / "scripts/vscode.zsh")],
            input=answers, text=True, capture_output=True, env=environment,
            cwd=directory, timeout=10,
        )
        return result, log.read_text().splitlines() if log.exists() else []

    def test_declining_setup_installs_nothing(self):
        result, calls = self.run_setup("n\n")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(calls, [])

    def test_only_accepted_extensions_are_installed(self):
        result, calls = self.run_setup("y\ny\n" + "n\n" * 16)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls, ["--install-extension formulahendry.auto-close-tag"])

    def test_failure_names_the_extension_and_stops(self):
        result, calls = self.run_setup("y\ny\n" + "y\n" * 16, fail=True)
        self.assertEqual(result.returncode, 7)
        self.assertIn("formulahendry.auto-close-tag", result.stderr)
        self.assertIn("7", result.stderr)
        self.assertEqual(calls, ["--install-extension formulahendry.auto-close-tag"])


if __name__ == "__main__":
    unittest.main()
