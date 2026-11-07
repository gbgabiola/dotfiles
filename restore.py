#!/usr/bin/env python3
"""Restore entries from one sync snapshot into an existing home directory."""

import argparse
import os
from pathlib import Path
import sys

from sync import ROOT, managed_link


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
        previous_link = None
        if os.path.lexists(target):
            if not managed_link(target, source / saved.name):
                print(f"Skipped unrelated entry: {target}", file=sys.stderr)
                continue
            previous_link = os.readlink(target)
            target.unlink()

        try:
            saved.rename(target)
        except OSError:
            if previous_link is not None and not os.path.lexists(target):
                target.symlink_to(previous_link)
            raise
        print(f"Restored: {target}")


if __name__ == "__main__":
    try:
        main()
    except OSError as exc:
        sys.exit(f"restore: {exc}")
