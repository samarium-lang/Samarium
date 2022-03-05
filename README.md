# Samarium

Samarium is a dynamic interpreted language transpiled to Python.
Samarium, in its most basic form, doesn't use any digits or letters.

Here's a `Hello, World!` program written in Samarium:

<span style="display: inline-block" align="left">
    <img src="docs/images/00helloworld.png" width="50%">
</span>

Note: Every statement in Samarium must end in a semicolon.

The following guide assumes that you are familiar with the basics of programming.

# Table of Contents

- [Variables](docs/00variables.md)
  - [Null](docs/00variables.md#null)
  - [Constants](docs/00variables.md#constants)
- [Integers](docs/01integers.md)
  - [Random Numbers](docs/01integers.md#random-numbers)
- [Operators](docs/02operators.md)
  - [Arithmetic](docs/02operators.md#arithmetic)
  - [Comparison](docs/02operators.md#comparison)
  - [Logic and Membership](docs/02operators.md#logic-and-membership)
  - [Bitwise](docs/02operators.md#bitwise)
  - [Assignment](docs/02operators.md#assignment)
- [Strings](docs/03strings.md)
- [Arrays](docs/04arrays.md)
  - [Array Comprehension](docs/04arrays.md#array-comprehension)
- [Tables](docs/05tables.md)
  - [Table Comprehension](docs/05tables.md#table-comprehension)
- [Slices](docs/06slices.md)
- [Comments](docs/07comments.md)
- [Built-in Functions](docs/08builtins.md)
  - [STDIN](docs/08builtins.md#stdin)
  - [STDOUT](docs/08builtins.md#stdout)
  - [STDERR](docs/08builtins.md#stderr)
  - [EXIT](docs/08builtins.md#exit)
  - [HASH](docs/08builtins.md#hash)
  - [TYPEOF](docs/08builtins.md#typeof)
  - [CAST](docs/08builtins.md#cast)
  - [SPECIAL](docs/08builtins.md#special)
  - [DTNOW](docs/08builtins.md#dtnow)
  - [SLEEP](docs/08builtins.md#sleep)
  - [ASSERT](docs/08builtins.md#assert)
  - [PARENT](docs/08builtins.md#parent)
- [Control Flow](docs/09controlflow.md)
  - [`if`/`else`](docs/09controlflow.md#ifelse)
  - [`foreach` loop](docs/09controlflow.md#foreach-loop)
  - [`while` loop](docs/09controlflow.md#while-loop)
  - [`break`/`continue`](docs/09controlflow.md#breakcontinue)
  - [`try`/`catch`](docs/09controlflow.md#trycatch)
- [Functions](docs/10functions.md)
  - [Main Function](docs/10functions.md#main-function)
  - [Default Arguments](docs/10functions.md#default-arguments)
- [Modules](docs/11modules.md)
  - [Importing](docs/11modules.md#importing)
- [Classes](docs/12classes.md)
- [File I/O](docs/13fileio.md)
  - [Creating](docs/13fileio.md#creating)
  - [Reading](docs/13fileio.md#reading)
  - [Writing](docs/13fileio.md#writing)
  - [Appending](docs/13fileio.md#appending)
  - [Closing](docs/13fileio.md#closing)
  - [Quick Operations](docs/13fileio.md#quick-operations)
- Standard Library
  - [`collections` module](docs/14stdcollections.md)
  - [`iter` module](docs/15stditer.md)
  - [`math` module](docs/16stdmath.md)
  - [`random` module](docs/17stdrandom.md)
  - [`string` module](docs/18stdstring.md)
  - [`types` module](docs/19stdtypes.md)


# Credits

Samarium was inspired by several languages, including [brainfuck](https://esolangs.org/wiki/Brainfuck), [Rust](https://www.rust-lang.org/), [Java](https://www.java.com/) and [Python](https://www.python.org/).
Thanks to [tetraxile](https://github.com/tetraxile) for helping with design choices and writing the docs, and [DarviL82](https://github.com/DarviL82) for fixing some issues.