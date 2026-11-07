#!/usr/bin/env zsh
# Update only this dotfiles checkout, then reconcile its home links.
set -eu

if (( EUID == 0 )); then
  print -u2 'Run this updater as your regular user, without sudo.'
  exit 1
fi

if (( $# > 1 )); then
  print -u2 'Usage: zsh scripts/update.zsh [checkout]'
  exit 2
fi

repo_dir=${1:-${0:A:h:h}}
cd -- "$repo_dir"
if [[ ! -f install.sh || ! -f sync.py || ! -d home ]]; then
  print -u2 'Expected a dotfiles checkout.'
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  print -u2 'Python 3 is required to sync dotfiles.'
  exit 1
fi

changes=$(git status --porcelain)
if [[ -n "$changes" ]]; then
  print -u2 'The checkout has local changes. Commit or stash them before updating.'
  exit 1
fi

git pull --ff-only
exec bash ./install.sh
