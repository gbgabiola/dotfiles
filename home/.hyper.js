// Future versions of Hyper may add additional config options,
// which will not automatically be merged into this file.
// See https://hyper.is#cfg for all currently supported options.

module.exports = {
  config: {
    // choose either `'stable'` for receiving highly polished,
    // or `'canary'` for less polished but more frequent updates
    updateChannel: 'stable',

    // default font size in pixels for all tabs
    fontSize: 14,

    // font family with optional fallbacks
    fontFamily: '"Fira Code", "UbuntuMono NF", Menlo, monospace',

    // default font weight: 'normal' or 'bold'
    fontWeight: 'normal',

    // font weight for bold characters: 'normal' or 'bold'
    fontWeightBold: 'bold',

    // terminal cursor background color and opacity (hex, rgb, hsl, hsv, hwb or cmyk)
    cursorColor: 'rgba(248,28,229,0.8)',

    // terminal text color under BLOCK cursor
    cursorAccentColor: '#000',

    // `'BEAM'` for |, `'UNDERLINE'` for _, `'BLOCK'` for █
    // cursorShape: 'BLOCK',
    cursorShape: 'BLOCK',

    // set to `true` (without backticks and without quotes) for blinking cursor
    cursorBlink: true,

    // color of the text
    foregroundColor: '#fff',

    // terminal background color
    // opacity is only supported on macOS
    backgroundColor: '#000',

    // terminal selection color
    selectionColor: 'rgba(248,28,229,0.3)',

    // border color (window, tabs)
    borderColor: '#333',

    // custom CSS to embed in the main window
    // Custom CSS to remove header/window-controls and adjust styling
    css: '',
    // css: `
    //   .terms_19b1ydh {
    //     margin-top: 20px;
    //   }
    //   .header_windowHeader {
    //   	display: none;
    //   }
    //   .tabs_nav {
    //   	top: 0;
    //   }
    //   .terms_terms {
    //   	margin-top: 0;
    //   }
    //   .terms_termsShifted {
    //   	margin-top: 30px;
    //   },
    // `,

    // custom CSS to embed in the terminal window
    termCSS: '',

    // if you're using a Linux setup which show native menus, set to false
    // default: `true` on Linux, `true` on Windows, ignored on macOS
    showHamburgerMenu: '',

    // set to `false` (without backticks and without quotes) if you want to hide the minimize, maximize and close buttons
    // additionally, set to `'left'` if you want them on the left, like in Ubuntu
    // default: `true` (without backticks and without quotes) on Windows and Linux, ignored on macOS
    showWindowControls: '',

    // custom padding (CSS format, i.e.: `top right bottom left`)
    padding: '12px 14px',

    // the full list. if you're going to provide the full color palette,
    // including the 6 x 6 color cubes and the grayscale map, just provide
    // an array here instead of a color map object
    colors: {
      black: '#000000',
      red: '#C51E14',          // #ff0000
      green: '#1DC121',        // #33ff00
      yellow: '#C7C329',       // #ffff00
      blue: '#0A2FC4',         // #0066ff
      magenta: '#C839C5',      // #cc00ff
      cyan: '#20C5C6',         // #00ffff
      white: '#C7C7C7',        // #d0d0d0
      lightBlack: '#686868',   // #808080
      lightRed: '#FD6F6B',     // #ff0000
      lightGreen: '#67F86F',   // #33ff00
      lightYellow: '#FFFA72',  // #ffff00
      lightBlue: '#6A76FB',    // #0066ff
      lightMagenta: '#FD7CFC', // #cc00ff
      lightCyan: '#68FDFE',    // #00ffff
      lightWhite: '#FFFFFF',   // #ffffff
    },

    // the shell to run when spawning a new session (i.e. /usr/local/bin/fish)
    // if left empty, your system's login shell will be used by default
    //
    // Windows
    // - Make sure to use a full path if the binary name doesn't work
    // - Remove `--login` in shellArgs
    //
    // Bash on Windows
    // shell: `C:\\Windows\\System32\\bash.exe`
    //
    // PowerShell on Windows
    // - Example: `C:\\WINDOWS\\System32\\WindowsPowerShell\\v1.0\\powershell.exe`
    //
    // Git shell on Windows
    // - Example: 'C:\\Program Files\\Git\\git-cmd.exe',
    shell: 'wsl.exe',

    // for setting shell arguments (i.e. for using interactive shellArgs: `['-i']`)
    // by default `['--login']` will be used
    // shellArgs: ['--login'],
    // shellArgs: ['--login', '-i', '/c wsl'],
    shellArgs: [],

    // for environment variables
    env: {},

    // set to `false` for no bell
    bell: 'SOUND',

    // if `true` (without backticks and without quotes), selected text will automatically be copied to the clipboard
    copyOnSelect: true,

    // if `true` (without backticks and without quotes), hyper will be set as the default protocol client for SSH
    defaultSSHApp: true,

    // if `true` (without backticks and without quotes), on right click selected text will be copied or pasted if no
    // selection is present (`true` by default on Windows and disables the context menu feature)
    // quickEdit: true,

    // URL to custom bell
    // bellSoundURL: 'http://example.com/bell.mp3',

    // for advanced config flags please refer to https://hyper.is/#cfg
  },

  // a list of plugins to fetch and install from npm
  // format: [@org/]project[#version]
  // examples:
  //   `hyperpower`
  //   `@company/project`
  //   `project#1.0.1`
  plugins: [
    // 'hyperterm-atom-dark',
    'hyper-material-theme',
    // 'hyperterm-material-dark',
    // 'hyperterm-cobalt2-theme',
    'hyperterm-paste',
    'hyperlinks', // Automatically formats URLs into hyperlinks
    'hyperterm-tabs', //  Adds shortcut keys to reorder your tabs!
    ],

  // in development, you can create a directory under
  // `~/.hyper_plugins/local/` and include it here
  // to load it and avoid it being `npm install`ed
  localPlugins: [],

  keymaps: {
    // Example
    // 'window:devtools': 'cmd+alt+o',
  },
};
