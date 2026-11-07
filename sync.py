#!/usr/bin/env python3
"""Link the repository's home files, saving any approved replacements."""

import argparse
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
LOCAL_FILES = {".localrc", ".gitlocal"}


def managed_link(target, source):
    # Compare link paths without following the source entry itself.
    return target.is_symlink() and Path(
        os.path.abspath(target.parent / os.readlink(target))
    ) == source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", type=Path, default=ROOT / "home")
    parser.add_argument("destination", nargs="?", type=Path, default=Path.home())
    parser.add_argument("backup", nargs="?", type=Path, default=ROOT / "backup")
    parser.add_argument("--dry-run", action="store_true", help="preview without writing")
    args = parser.parse_args()

    source = (ROOT / args.source.expanduser()).resolve()
    destination = args.destination.expanduser().resolve()
    backup = (ROOT / args.backup.expanduser()).resolve()
    if not source.is_dir() or not destination.is_dir():
        parser.error("source and destination must be existing directories")
    if source == destination or source in backup.parents or backup == source:
        parser.error("source must be separate from the destination and backup")

    entries = [
        entry for entry in sorted(source.iterdir())
        if entry.name not in LOCAL_FILES and not entry.name.endswith(".example")
    ]
    snapshot = None
    for entry in entries:
        target = destination / entry.name
        if target in source.parents or backup == target or target in backup.parents:
            parser.error(f"destination entry overlaps the source or backup: {target}")

    for entry in entries:
        target = destination / entry.name
        if managed_link(target, entry):
            continue
        conflict = target.is_symlink() or target.exists()
        if args.dry_run:
            action = "Would back up and replace" if conflict else "Would link"
            print(f"{action}: {target} -> {entry}")
            continue

        saved = None
        if conflict:
            if not sys.stdin.isatty() or input(
                f"Back up and replace {target}? [y/N] "
            ).strip().lower() not in {"y", "yes"}:
                print(f"Skipped: {target}", file=sys.stderr)
                continue
            if snapshot is None:
                backup.mkdir(parents=True, exist_ok=True)
                snapshot = Path(tempfile.mkdtemp(prefix="sync-", dir=backup))
                print(f"Backup snapshot: {snapshot}")
            saved = snapshot / target.name
            target.rename(saved)

        try:
            target.symlink_to(os.path.relpath(entry, destination))
        except OSError:
            if saved is not None and not os.path.lexists(target):
                saved.rename(target)
            raise
        print(f"Linked: {target} -> {entry}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, EOFError) as exc:
        sys.exit(f"sync: {exc}")
