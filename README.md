# Samarium

Samarium is a dynamic interpreted language transpiled to Python.
Samarium, in its most basic form, doesn't use any digits or letters.

Here's a `Hello, World!` program written in Samarium:

<span style="display: inline-block" align="left">
    <img src="docs/images/00helloworld.png" width="50%">
</span>

Note: Every statement in Samarium must end in a semicolon, and backticks will be ignored.

Documentation on how to program in Samarium can be found [here](docs/tableofcontents.md).


# Installation

## [pip](https://pypi.org/project/pip/)

`pip install samarium`

## [AUR](https://aur.archlinux.org/)

`yay -S samarium`

## Using Samarium

You can run Samarium programs with `samarium program.sm`.
`samarium-debug` may be used instead, which will first print out the intermediary Python code that the Samarium program is transpiled into, before executing it.

The `-c <command>` option can be used to execute Samarium code from the string `command`, directly in the terminal.
`command` can be one or more statements separated by semicolons as usual.
Note that the last statement of `command` will be printed if it does not end in a semicolon.

There is also a VSCode syntax highlighting extension for Samarium, which can be found here [here](https://marketplace.visualstudio.com/items?itemName=Samarium.samarium-language). The source code can be found [here](https://github.com/samarium-lang/vscode-samarium).


# Credits

Samarium was inspired by several languages, including [brainfuck](https://esolangs.org/wiki/Brainfuck), [Rust](https://www.rust-lang.org/), [Java](https://www.java.com/) and [Python](https://www.python.org/).
Thanks to [tetraxile](https://github.com/tetraxile) for helping with design choices and writing the docs, [MithicSpirit](https://github.com/MithicSpirit) for making Samarium an AUR package, and [DarviL82](https://github.com/DarviL82) for fixing some issues.

If you have any questions, or would like to get in touch, join the [Discord server](https://discord.gg/C8QE5tVQEq)!