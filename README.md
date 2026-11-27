# gbgabiola's dotfiles

[![README views](https://hits.sh/github.com/gbgabiola/dotfiles.svg?label=README%20views&color=006a60)](https://hits.sh/github.com/gbgabiola/dotfiles/)

Personal shell, Git, editor, and terminal settings for Ubuntu on WSL 2. Native
Ubuntu uses the same Linux setup. macOS and other Linux distributions are
untested.

## Install on Ubuntu or WSL

Run these commands in Ubuntu as your regular user. On WSL, keep the checkout
under your Linux home directory so the checkout and home directory share a
filesystem.

```sh
sudo apt update
sudo apt install git python3 zsh
git clone https://github.com/gbgabiola/dotfiles.git ~/.dotfiles
cd ~/.dotfiles
bash install.sh --dry-run
bash install.sh
```

The installer links entries from `home/` into your home directory. It skips
local overrides and templates. If a destination already exists, the installer
asks before replacing it and saves the original in a new `backup/sync-*`
directory. Noninteractive runs skip conflicts. You can rerun the installer:
existing links to the same checkout are kept. Backing up a conflict requires
the backup location and the destination to share a filesystem.

To use Zsh as your login shell, run `chsh -s "$(command -v zsh)"` once and
start a new login session. Package installation and Windows app setup are
separate from linking dotfiles.

## Personalize this machine

If an older install linked `~/.localrc` to a tracked file, make it a regular
file **before** updating the checkout. From Ubuntu, run:

```sh
if [ -L "$HOME/.localrc" ] && [ -f "$HOME/.localrc" ]; then
  tmp=$(mktemp "$HOME/.localrc.XXXXXX") &&
    cp -- "$HOME/.localrc" "$tmp" &&
    mv -f -- "$tmp" "$HOME/.localrc"
fi
```

If the old link is already dangling, inspect it with `ls -l ~/.localrc`, remove
the link with `unlink ~/.localrc`, then use the template below.

- **Zsh overrides:** Copy `home/.localrc.example` to `~/.localrc` if you don't
  already have one. Add editor, locale, or machine-specific environment
  settings there. Zsh reads it at the end of `home/.zshrc`.
- **Git identity:** The `[include]` block at the end of `home/.gitconfig` reads
  `~/.gitlocal`. Set your identity there and remove any old
  `GIT_AUTHOR_NAME` or `GIT_AUTHOR_EMAIL` exports from `~/.localrc` so they
  don't override the Git settings.

```sh
git config --file ~/.gitlocal user.name "Your Name"
git config --file ~/.gitlocal user.email "you@example.com"
```

## Optional development tools

Run `zsh scripts/nodejs.zsh` to install nvm and the current Node.js LTS.
The nvm release is pinned near the top of that script. To load nvm in new
Zsh sessions, add this to your own `~/.localrc`:

```sh
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
[ ! -s "$NVM_DIR/nvm.sh" ] || . "$NVM_DIR/nvm.sh"
```

For a project that needs a separate Python version, install the
[pyenv build dependencies](https://github.com/pyenv/pyenv/wiki#suggested-build-environment)
first. Then run `zsh scripts/python.zsh` for the latest Python 3.15 patch
known to your pyenv, or pass another version such as `3.14`. The script
pins pyenv for new installs and reuses an existing installation. It leaves
your global Python selection in place.

To make pyenv available in Zsh, add this to your own `~/.localrc`:

```zsh
export PYENV_ROOT="${PYENV_ROOT:-$HOME/.pyenv}"
[[ ! -d "$PYENV_ROOT/bin" ]] || path=("$PYENV_ROOT/bin" "${path[@]}")
if command -v pyenv >/dev/null 2>&1; then
  eval "$(pyenv init - zsh)"
fi
```

Open a new shell and run the `pyenv local` command printed by the installer
from the project directory.

## Update and restore

From your checkout, run `zsh scripts/update.zsh`. It requires a clean
checkout with an upstream branch, pulls with `--ff-only`, and reruns the
installer. Update Ubuntu packages and language tooling separately.

To undo replacements made during a sync, use the snapshot path printed by
the installer:

```sh
python3 restore.py backup/sync-REPLACE-WITH-YOUR-SNAPSHOT
```

Restore moves the saved entries back, consuming those entries from the
snapshot. It skips any destination that is neither missing nor still linked to
this checkout. New links that replaced nothing have no backup; remove those
links individually if you no longer want them. Keep the checkout in place
while its links are in use.

Restore requires Linux with filesystem support for atomic no-replace renames.
Keep the snapshot and destination on the same filesystem. If another process
creates or replaces a destination during restore, the backup is kept and
restore reports an error. A temporary recovery path is printed before moving
a managed link. If automatic rollback cannot put that entry back, the entry
remains at the printed path beside the snapshot. Inspect both paths before
resolving the conflict and retrying. After an interrupted run, check the
printed recovery path as well as the snapshot.

## Configuration files

| File or directory | Where to apply changes |
| --- | --- |
| `home/` | Shared home files managed by the installer. Add personal shell overrides to `~/.localrc` and Git identity to `~/.gitlocal`. |
| `windows-terminal/settings.json` | Merge into Windows Terminal's settings JSON. The default profile is `Ubuntu-WSL`, with optional `ddev` and Git Bash profiles. Adapt profile GUIDs to your installed profiles. |
| `vscode/User/settings.json` | Merge into VS Code User Settings (JSON), or Remote Settings (JSON) for WSL-specific settings. Review the Windows Terminal executable path and installed shell profiles. |
| `Startup/hotkeys.ahk` | AutoHotkey v1-style reference. Replace application and folder paths, or remove unused hotkeys before enabling it. |
| `.wslconfig` | Merge selected settings into `%UserProfile%/.wslconfig` on Windows. |
| `etc/wsl.conf` | Merge selected settings into `/etc/wsl.conf` inside Ubuntu. Its `root = /` setting mounts the C drive at `/c` instead of the default `/mnt/c`. |
| `bin/` and `scripts/` | User commands and optional setup utilities. `server [port]` serves the current directory on `127.0.0.1`, using port 8000 by default. |

Install FiraCode NFM and Hack Nerd Font Mono, or select fonts already installed
on your machine. The VS Code reference uses Dracula and Material Icon Theme;
install them if you want to use those settings:

```sh
code --install-extension dracula-theme.theme-dracula
code --install-extension PKief.material-icon-theme
```

Run `zsh scripts/vscode.zsh` to choose additional extensions. The supplied
VS Code settings use manual application updates and disable automatic extension
checks and updates. Review updates manually in VS Code.

When removing or renaming a file under `home/`, inspect the corresponding
home-directory link. Sync does not prune old links. After updating from a
version that included the retired terminal configuration, inspect old links
before removing them, and only unlink entries that point into this checkout.

## Validation

With Python 3, Git, Vim, Bash, and Zsh installed, run from the checkout:

```sh
python3 -B -m unittest discover -s tests -v
```

Tests use temporary directories and stub privileged commands. Run as a regular
user so the installer integration tests execute. GitHub Actions runs the suite
and shell syntax checks for pull requests and pushes to main.

## Credits

- [@holman](https://github.com/holman)
- [@jldeen](https://github.com/jldeen)
- [@denysdovhan](https://github.com/denysdovhan)
- [@sapegin](https://github.com/sapegin)

## License

Copyright © 2019–2026 [gbgabiola](https://gbgabiola.vercel.app).

This repository is licensed under the [MIT License](LICENSE).
