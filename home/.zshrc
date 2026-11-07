#
# ~/.zshrc
#

# ------------------------------------------------------------------------------
# Environment
# ------------------------------------------------------------------------------

# Find the checkout even when ~/.zshrc is a symlink.
if [[ -z $DOTFILES ]]; then
  DOTFILES=${${(%):-%x}:A:h:h}
  [[ -f "$DOTFILES/sync.py" ]] || DOTFILES="$HOME/.dotfiles"
fi
export DOTFILES

# Do not override files using >, but allow >! to force it.
set -o noclobber

# Zsh ties the path array to PATH. Keep the first occurrence of each entry.
typeset -U path
for dir in "$HOME/.rvm/bin" "$HOME/.npm-global/bin" "$DOTFILES/bin" "$HOME/.bin"; do
  [[ -d "$dir" ]] && path=("$dir" "${path[@]}")
done
unset dir

if [[ -d "$HOME/.npm-global/lib/node_modules" ]]; then
  node_modules="$HOME/.npm-global/lib/node_modules"
  if [[ ":$NODE_PATH:" != *":$node_modules:"* ]]; then
    export NODE_PATH="${NODE_PATH:+$NODE_PATH:}$node_modules"
  fi
  unset node_modules
fi

# Default pager
export PAGER='less'

# less options
less_opts=(
  # Quit if entire file fits on first screen.
  --quit-if-one-screen
  # Ignore case in searches that do not contain uppercase.
  --ignore-case
  # Allow ANSI colour escapes, but no other escapes.
  --RAW-CONTROL-CHARS
  # Quiet the terminal bell. (when trying to scroll past the end of the buffer)
  --quiet
  # Do not complain when we are on a dumb terminal.
  --dumb
)
export LESS="${less_opts[*]}"

# Keep a caller-provided editor, otherwise use an installed terminal editor.
if [[ -z $EDITOR ]]; then
  if (( $+commands[vim] )); then
    EDITOR=vim
  else
    EDITOR=vi
  fi
fi
export EDITOR

export SSH_KEY_PATH="$HOME/.ssh/id_rsa"

if [[ -t 0 ]] && gpg_tty=$(tty); then
  export GPG_TTY="$gpg_tty"
fi
unset gpg_tty

# Machine-specific overrides run last.
if [[ -r "$HOME/.localrc" ]]; then
  source "$HOME/.localrc"
fi
