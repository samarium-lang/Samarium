# Samarium

Samarium is a dynamic interpreted language transpiled to Python.
Samarium, in its most basic form, doesn't use any digits or letters.

Here's a `Hello, World!` program written in Samarium:

```kt
"Hello, World!"!;
```

Documentation on how to program in Samarium can be found [here](https://samarium-lang.github.io/Samarium/).


# Installation

## [pip](https://pypi.org/project/pip/)

```sh
pip install samarium
```

## [AUR](https://aur.archlinux.org/)

```sh
git clone https://aur.archlinux.org/samarium.git && cd samarium && makepkg -sirc
```
or use your favorite [AUR helper](https://wiki.archlinux.org/title/AUR_helpers).

## Using Samarium

You can run Samarium programs with `samarium program.sm`.
`samarium-debug` may be used instead, which will first print out the intermediary Python code that the Samarium program is transpiled into, before executing it.

Short | Long | Description
:---: | :---: | :---
`-c <cmd>` | `--command <cmd>` | Can be used to execute Samarium code from the string `cmd`,<br>directly in the terminal. `cmd` can be one or more statements<br>separated by semicolons as usual. Note that the last statement<br> of `cmd` will be printed if it does not end in a semicolon.
`-h` | `--help` | Shows the help message
`-v` | `--version` | Prints Samarium version


There is also a VSCode syntax highlighting extension for Samarium, which can be found [here](https://marketplace.visualstudio.com/items?itemName=Samarium.samarium-language). The source code can be found [here](https://github.com/samarium-lang/vscode-samarium).


# Credits

Samarium was inspired by several languages, including [brainfuck](https://esolangs.org/wiki/Brainfuck), [Rust](https://www.rust-lang.org/), and [Python](https://www.python.org/).

Special thanks to:

- [tetraxile](https://github.com/tetraxile) for helping with design choices and writing the docs
- [MithicSpirit](https://github.com/MithicSpirit) for making an AUR package for Samarium
- [DarviL82](https://github.com/DarviL82) for fixing some issues
- [Endercheif](https://github.com/Endercheif) for making the documentation look fancy, helping with design choices, and adding partial Python Interoperability

If you have any questions, or would like to get in touch, join my [Discord server](https://discord.gg/C8QE5tVQEq)!
