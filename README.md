# Genesis Gabiola's dotfiles

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

## Where to make changes

| What | Where to edit or apply it |
| --- | --- |
| Shared shell settings | Edit `home/.zshrc`. Put environment and PATH changes near the top; keep the local override block last. |
| Shared Git settings | Edit the relevant section in `home/.gitconfig`. Add identity only to `~/.gitlocal`. |
| New shared home files | Add them to `home/` and preview with `bash install.sh --dry-run`. Put samples in files ending in `.example`. |
| Commands and tooling | Add commands to `bin/`; add standalone setup utilities to `scripts/`. |
| WSL settings | Review `.wslconfig` for the Windows user profile and `etc/wsl.conf` for `/etc/wsl.conf` inside Ubuntu. Merge only the settings you need. |
| Windows Terminal and VS Code | Use `windows-terminal/settings.json` and `vscode/User/` as references; merge the relevant settings into your app's existing configuration. |
| Windows startup | Review `Startup/` before applying its Windows startup files manually. |

If you delete or rename a file under `home/`, check the corresponding link
in your home directory. Sync does not prune links; remove the old link after
verifying it points into this checkout.

## Credits

- [@holman](https://github.com/holman)
- [@jldeen](https://github.com/jldeen)
- [@denysdovhan](https://github.com/denysdovhan)
- [@sapegin](https://github.com/sapegin)

MIT © [Genesis Gabiola](https://genesisgabiola.tech)
