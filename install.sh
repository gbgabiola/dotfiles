#!/usr/bin/env bash
# Link dotfiles from this checkout. Pass sync.py arguments through unchanged.
set -euo pipefail

if (( EUID == 0 )); then
  printf 'Run this installer as your regular user, without sudo.\n' >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  printf 'Python 3 is required. On Ubuntu, install it with: sudo apt install python3\n' >&2
  exit 1
fi

repo_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
exec python3 "$repo_dir/sync.py" "$@"
