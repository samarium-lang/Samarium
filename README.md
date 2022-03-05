# Samarium

Samarium is a dynamic interpreted language transpiled to Python.
Samarium, in its most basic form, doesn't use any digits or letters.

Here's a `Hello, World!` program written in Samarium:

<span style="display: inline-block" align="left">
    <img src="docs/images/00helloworld.png" width="50%">
</span>

Documentation on how to program in Samarium can be found [here](docs/tableofcontents.md).


# Installation

Samarium can be installed from [pip](https://pypi.org/project/pip/), by running `pip install samarium`.
You can then run Samarium programs with `samarium program.sm`.
`samarium-debug` may be used instead, which will first print out the intermediary Python code that the Samarium program is transpiled into, before executing it.

The `-c <command>` option can be used to execute Samarium code from the string `command`, directly in the terminal.
`command` can be one or more statements separated by semicolons as usual.
Note that the last statement of `command` will be printed if it does not end in a semicolon.


# Credits

Samarium was inspired by several languages, including [brainfuck](https://esolangs.org/wiki/Brainfuck), [Rust](https://www.rust-lang.org/), [Java](https://www.java.com/) and [Python](https://www.python.org/).
Thanks to [tetraxile](https://github.com/tetraxile) for helping with design choices and writing the docs, and [DarviL82](https://github.com/DarviL82) for fixing some issues.