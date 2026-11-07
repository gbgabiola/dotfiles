#!/usr/bin/env zsh

set -e

python_version=${1:-3.15}
if (( $# > 1 )) || [[ ! $python_version =~ '^3\.[0-9]+(\.[0-9]+)?$' ]]; then
  print -u2 'Usage: zsh scripts/python.zsh [3.minor[.patch]]'
  exit 2
fi

pyenv_version=v2.8.14
export PYENV_ROOT="${PYENV_ROOT:-$HOME/.pyenv}"

if [[ -x "$PYENV_ROOT/bin/pyenv" ]]; then
  pyenv_bin="$PYENV_ROOT/bin/pyenv"
elif command -v pyenv >/dev/null 2>&1; then
  pyenv_bin=$(command -v pyenv)
elif [[ -e "$PYENV_ROOT" || -L "$PYENV_ROOT" ]]; then
  print -u2 -- "Cannot install pyenv over $PYENV_ROOT. Choose a different PYENV_ROOT."
  exit 1
else
  git clone --depth 1 --branch "$pyenv_version" https://github.com/pyenv/pyenv.git "$PYENV_ROOT"
  pyenv_bin="$PYENV_ROOT/bin/pyenv"
fi

if ! release=$("$pyenv_bin" latest -k "$python_version"); then
  print -u2 -- "Update your pyenv installation or choose a known Python version."
  exit 1
fi

"$pyenv_bin" install -s "$release"
print -r -- "Python $release is installed. Run 'pyenv local $release' in a project to select it."
