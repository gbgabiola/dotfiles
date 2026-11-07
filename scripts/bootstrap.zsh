#!/usr/bin/env zsh

# Run the optional setup helpers from this checkout.
set -e

scripts_dir=${0:A:h}
zsh "$scripts_dir/nodejs.zsh"
zsh "$scripts_dir/vscode.zsh"
