#!/usr/bin/env zsh

set -e

read -r 'answer?Install nvm and the current Node.js LTS release? [y/N] '
if [[ $answer != [yY] ]]; then
  exit 0
fi

nvm_version=v0.41.0
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
installer=$(mktemp)
trap 'rm -f -- "$installer"' EXIT

curl -fsSL -o "$installer" "https://raw.githubusercontent.com/nvm-sh/nvm/$nvm_version/install.sh"
mkdir -p -- "$NVM_DIR"
PROFILE=/dev/null bash "$installer"
source "$NVM_DIR/nvm.sh"
nvm install --lts
