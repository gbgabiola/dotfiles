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

### Notes
Your dotfiles are how you personalize your System environment.

> If you're interested in the philosophy behind why projects like these are awesome, you might want to [read zach post on the subject](http://zachholman.com/2010/08/dotfiles-are-meant-to-be-forked/).

If you need to learn how to install Ubuntu on Windows or Windows Subsystem for Linux, take a look at this [Microsoft Guide](https://msdn.microsoft.com/en-us/commandline/wsl/install_guide)


## Bugs
Dotfiles must be updated every now and then, that means if I forgot to check the requirements or dependencies, there's a good chance it can break something.

If you run into any blockers or error please [open an issue](https://github.com/genesisgabiola/dotfiles/issues) on this repository, and I would try to fix it as soon as possible for you.


## Resources
I'll be adding more resources soon, update regularly, and give back the credits to the other creators.

- [dotfiles](http://dotfiles.github.com/)
- [Oh My ZSH](http://ohmyz.sh/)
- [Powerline fonts](https://github.com/powerline/fonts)
- [Spaceships ZSH](https://github.com/denysdovhan/spaceship-prompt)

## Credits
- [@holman](https://github.com/holman)
- [@jldeen](https://github.com/jldeen)
- [@denysdovhan](https://github.com/denysdovhan)
- [@sapegin](https://github.com/sapegin)

## License
MIT © [Genesis Gabiola](https://genesisgabiola.netlify.com)
