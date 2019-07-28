# Genesis Gabiola's dotfiles

## Installation
Install by running one of the following commands by just copying and then execute it in the terminal:

**via `curl`**
```sh
bash -c "$(curl -fsSL https://raw.githubusercontent.com/genesisgabiola/dotfiles/master/installer.sh)"
```

**via `wget`**
```sh
bash -c "$(wget https://raw.githubusercontent.com/genesisgabiola/dotfiles/master/installer.sh -O -)"
```

```sh
$ git clone https://github.com/genesisgabiola/dotfiles.git ~/.dotfiles
$ sudo ~/.dotfiles/install.sh

# or
$ chmod +x install.sh
$ ./install.sh
```

This will symlink the appropriate files in `.dotfiles` to your home directory.  
Everything is configured and tweaked within `~/.dotfiles`.

Tell Git who you are using these commands:
```sh
git config -f ~/.gitlocal user.email "email@yoursite.com"
git config -f ~/.gitlocal user.name "FirstName LastName"
```

## Updating
Use `update` command to get latest updates:
```sh
update
```

This command will update dotfiles, their dependencies, `apt-get` packages, global `npm` dependencies, and optional for `gems`.



## License
MIT © [Genesis Gabiola](https://genesisgabiola.netlify.com)
