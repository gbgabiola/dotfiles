"""Regression tests for Vim's :W command without invoking real sudo."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VIM = shutil.which("vim")
SHELLS = [
    executable
    for name in ("sh", "bash", "zsh")
    if (executable := shutil.which(name))
]


@unittest.skipUnless(VIM, "Vim is required for privileged-save regression tests")
class PrivilegedSaveTests(unittest.TestCase):
    def save(self, directory, filename, shell, fail=False):
        target = directory / filename
        target.write_text("original\n", encoding="utf-8")
        binary_directory = directory / "bin"
        binary_directory.mkdir()
        sudo = binary_directory / "sudo"
        sudo.write_text(
            '#!/bin/sh\n'
            'printf "%s\\0" "$@" > "$SUDO_LOG"\n'
            'if [ "$FAIL_SUDO" = 1 ]; then exit 1; fi\n'
            'exec "$@"\n',
            encoding="utf-8",
        )
        sudo.chmod(0o755)
        script = directory / "save.vim"
        script.write_text(
            "let &shell = $TEST_SHELL\n"
            "execute 'edit ' . fnameescape($TEST_TARGET)\n"
            "call setline(1, 'changed')\n"
            "W\n"
            "call writefile([string(v:shell_error)], $TEST_STATUS)\n"
            "qa!\n",
            encoding="utf-8",
        )
        environment = os.environ.copy()
        environment.update(
            HOME=str(directory),
            SHELL=shell,
            PATH=str(binary_directory) + os.pathsep + environment["PATH"],
            TEST_SHELL=shell,
            TEST_TARGET=str(target),
            TEST_STATUS=str(directory / "status"),
            SUDO_LOG=str(directory / "sudo-arguments"),
            FAIL_SUDO="1" if fail else "0",
        )
        result = subprocess.run(
            [VIM, "-Nu", str(ROOT / "home/.vimrc"), "-i", "NONE", "-n",
             "-es", "-S", str(script)],
            cwd=directory,
            env=environment,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        arguments = (directory / "sudo-arguments").read_bytes().split(b"\0")[:-1]
        self.assertEqual(arguments, [b"tee", b"--", os.fsencode(target)])
        self.assertEqual(
            (directory / "status").read_text().strip(),
            "1" if fail else "0",
        )
        self.assertEqual(target.read_text(), "original\n" if fail else "changed\n")
        self.assertFalse((directory / "marker").exists())
        return target

    def test_filenames_are_passed_literally(self):
        filenames = (
            "ordinary.txt",
            "file with spaces.txt",
            "single'quote.txt",
            'double"quote.txt',
            "file; touch marker",
            "file$(touch marker)",
            "file`touch marker`",
            "percent%.txt",
            "hash#.txt",
            "bang!.txt",
            "pipe|name.txt",
            "-leading-option",
            "line\nbreak.txt",
        )
        for shell in SHELLS:
            for filename in filenames:
                with self.subTest(shell=shell, filename=filename):
                    with tempfile.TemporaryDirectory(prefix="vim-save-") as temporary:
                        directory = Path(temporary)
                        target = self.save(directory, filename, shell)
                        self.assertEqual(
                            set(directory.iterdir()),
                            {
                                target,
                                directory / "bin",
                                directory / "save.vim",
                                directory / "status",
                                directory / "sudo-arguments",
                            },
                        )

    def test_failed_sudo_preserves_the_existing_file(self):
        for shell in SHELLS:
            with self.subTest(shell=shell):
                with tempfile.TemporaryDirectory(prefix="vim-save-") as temporary:
                    self.save(Path(temporary), "file with spaces.txt", shell, fail=True)


if __name__ == "__main__":
    unittest.main()
