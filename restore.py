#!/usr/bin/env python3
"""Restore entries from one sync snapshot into an existing home directory."""

import argparse
import ctypes
import errno
import os
from pathlib import Path
import sys
import tempfile

from sync import ROOT, managed_link


def move_without_overwrite(source, destination):
    """Atomically move an entry only when its destination is absent."""
    try:
        rename = ctypes.CDLL(None, use_errno=True).renameat2
    except AttributeError:
        raise OSError(
            errno.ENOTSUP, "Safe restore requires Linux renameat2 support"
        ) from None
    rename.argtypes = [
        ctypes.c_int, ctypes.c_char_p,
        ctypes.c_int, ctypes.c_char_p, ctypes.c_uint,
    ]
    rename.restype = ctypes.c_int
    at_fdcwd = -100
    rename_noreplace = 1
    if rename(
        at_fdcwd, os.fsencode(source),
        at_fdcwd, os.fsencode(destination), rename_noreplace,
    ) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(destination))


def restore_entry(saved, target, source):
    if not os.path.lexists(target):
        move_without_overwrite(saved, target)
        return True
    if not managed_link(target, source):
        print(f"Skipped unrelated entry: {target}", file=sys.stderr)
        return False

    # Preserve the actual entry before checking it again. A concurrent writer
    # may have replaced the managed link since the initial check.
    recovery = Path(tempfile.mkdtemp(prefix="restore-", dir=saved.parent.parent))
    held = recovery / target.name
    print(f"Recovery staging path: {held}", flush=True)
    try:
        move_without_overwrite(target, held)
        if not held.is_symlink() or Path(
            os.path.abspath(target.parent / os.readlink(held))
        ) != source:
            raise FileExistsError(
                errno.EEXIST, "Destination changed during restore", str(target)
            )
        move_without_overwrite(saved, target)
        held.unlink()
    except OSError:
        if os.path.lexists(held):
            try:
                move_without_overwrite(held, target)
            except OSError:
                print(f"Previous destination preserved at: {held}", file=sys.stderr)
        raise
    finally:
        # A nonempty recovery directory contains data needed for recovery.
        try:
            recovery.rmdir()
        except OSError:
            pass
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--destination", type=Path, default=Path.home())
    parser.add_argument("--source", type=Path, default=ROOT / "home")
    args = parser.parse_args()
    snapshot = args.snapshot.expanduser().resolve()
    destination = args.destination.expanduser().resolve()
    source = args.source.expanduser().resolve()
    if not snapshot.is_dir() or not destination.is_dir():
        parser.error("snapshot and destination must be existing directories")
    if (snapshot in destination.parents or snapshot in source.parents
            or source in snapshot.parents or snapshot == destination
            or snapshot == source or destination == source):
        parser.error("snapshot, source, and destination must be separate")

    for saved in sorted(snapshot.iterdir()):
        target = destination / saved.name
        if target in snapshot.parents or target in source.parents:
            parser.error(f"destination entry overlaps the snapshot or source: {target}")

    for saved in sorted(snapshot.iterdir()):
        target = destination / saved.name
        if restore_entry(saved, target, source / saved.name):
            print(f"Restored: {target}")


if __name__ == "__main__":
    try:
        main()
    except OSError as exc:
        sys.exit(f"restore: {exc}")
