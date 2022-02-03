# Samarium

Samarium is a dynamic interpreted language transpiled to Python.
Samarium, in its most basic form, doesn't use any digits or letters.

Here's a `Hello, World!` program written in Samarium:
<p align="left"><span style="display: inline-block">
    <img src="images/00helloworld.png" width="50%">
</span></p>

Note: Every statement in Samarium must end in a semicolon.

The following guide assumes that you are familiar with the basics of programming.


# Table of Contents
- [Introduction](#introduction)
- [Table of Contents](#table-of-contents)
- [Variables](#variables)
- [Numbers](#numbers)
- [Operators](#operators)
- [Strings](#strings)
- [Arrays](#arrays)
- [Tables](#tables)
- [Slices](#slices)
- [Comments](#comments)
- [Built-in Functions](#built-in-functions)
- [Control Flow](#control-flow)
- [Functions](#functions)
- [Importing](#importing)
- [Classes](#classes)
- [File I/O](#file-io)
- [Standard Library](#standard-library)


# Variables

Variables are defined using the assignment operator `:`, like so:
```
myVar: /;
```
Variables may be integers, strings, arrays, tables, or null.
Only letters and numbers can be used for variable names, thus camelCase is recommended for names consisting of multiple words.

## Null

The character `_` represents a null value, such as for default arguments in a function.
Assignments to `_` are not allowed.

## Constant Variables

Variables can be made constant by prefixing them with `<>`.
Any attempt to assign a new value to a constant variable will raise a `TypeError`.
```
<>x: //;
x: \;
```
This example raises `[TypeError] object is immutable`.


# Numbers

Numbers are represented in base 2, using slashes and backslashes to represent 1 and 0 respectively.
Only integers are supported in Samarium.
Negative numbers are represented as normal, with a `-` sign before them.

Let's see some examples of numbers:

Base 10 | Base 2  | Samarium
---     | ---     | --- 
`0`     | `0`     | `\`
`1`     | `1`     | `/`
`2`     | `10`    | `/\`
`3`     | `11`    | `//`
`5`     | `101`   | `/\/`
`8`     | `1000`  | `/\\\`
`13`    | `1101`  | `//\/`
`21`    | `10101` | `/\/\/`

Since Samarium is transpiled to Python, there's no limit to how large a number can be:

```
//\\/\\//////\\\\///\\////\\/\\/\\\\\\/////\\\\\\\\/////\\//\\/\\////\\////////\\////\\///\\\\\\\\//\\\\//\\///\\/\\\\\\/\\////\\//\\\\/\\\\/\\////\\/////\\/\\\\/\\\\\\\\\\//\\\\\\//\\\\/\\/\\\\//\\\\\\///\\/\\\\\\/\\\\\\/\\\\///\\//\\\\/\\\\//\\\\///\\//\\\\\\\\\\\\////////////////////////////////////////////////////////////////////////////////
```
Or in base 10: 
```py
99999999999999999999999999999999999999999999999999999999999999999999999999999999
```

## Random Numbers

A random number in a particular range can be generated using `^^`, like so:

`^^/ -> /\/\^^` generates a random integer from 1 to 10 inclusive.

More random number generation-related functions can be found in the [`random` module](#random-module)


# Operators

## Arithmetic

Operator | Meaning
---      | ---
`+`      | Addition
`-`      | Subtraction
`++`     | Multiplication
`--`     | Integer division
`+++`    | Exponentiation
`---`    | Modulo

## Comparison

Operator | Meaning
---      | ---
`<`      | Less than
`>`      | Greater than
`<:`     | Less than or equal to
`>:`     | Greater than or equal to
`::`     | Equal to
`:::`    | Not equal to

## Logic and Membership

Operator | Meaning
---      | ---
`&&`     | Logical AND
`\|\|`   | Logical OR
`~~`     | Logical NOT
`->?`    | `x ->? y` is equivalent to `x in y` in Python

## Bitwise

Operator | Meaning
---      | ---
`&`      | Bitwise AND
`\|`     | Bitwise OR
`~`      | Bitwise NOT
`^`      | Bitwise XOR

## Assignment

All arithmetic and bitwise operators (except `~`) can be used together with the assignment operator.

For example:
```
x: x - /\/;
x: x ++ //;
x: x --- /\\;
```
is equivalent to:
```
x-: /\/;
x++: //;
x---: /\\;
```


# Strings

Strings are defined using double quotation marks:
```rs
"Hello!"
```
Multiline strings do not require any additional syntax:
```rs
"This
is a
multiline
string"
```

Strings can be manipulated using some arithmetic operators:

`"hello" + "world"` is the same as  `"helloworld"`

`"hello" ++ //` is the same as `"hellohellohello"`


# Arrays

Arrays are defined using square brackets:
```
[\, \/, \\]
```

Arrays can be concatenated with the `+` operator:

`[/, //] + [/\]` is the same as `[/, //, /\]`

Elements can also be removed (by index) from an array using the `-` operator:

`[/, //\, /\, //] - /` gives `[/, /\, //]`


# Tables

Tables are defined using double curly brackets:
```hs
{{"key" -> "value", / -> //\}}
```


# Slices

Slices are used to access a range of elements in an iterable (strings, arrays, keys of a table).
They don't do anything by themselves.
Slices are enclosed in double angle brackets.
They have three parameters, `start`, `stop` and `step`, any of which may be omitted.
`..` is used to indicate `stop`, and `**` is used to indicate `step`.
```hs
str: "abcdefgh";
str<<\>> :: "a";
str<<//..//\>> :: "def";
str<</..//\**/\>> :: "bdf";
```

All valid slice parameters are as follows:
Slice                   | Returns
---                     | ---
`<<>>`                  | the whole iterable
`<<index>>`             | the element at position `index`
`<<..stop>>`            | all elements up to index `stop`
`<<**step>>`            | all elements separated by gaps of size `step`
`<<start..>>`           | all elements starting from index `start`
`<<..stop**step>>`      | all elements up to index `stop` separated by gaps of size `step`
`<<start**step>>`       | all elements starting from index `start` separated by gaps of size `step`
`<<start..stop>>`       | all elements starting from index `start` up to index `stop`
`<<start..stop**step>>` | all elements starting from index `start` up to index `stop` separated by gaps of size `step`


# Comments

Comments are written using `==`, and comment blocks are written with `==<` and `>==`:
```
== single-line comment

==< comment block
doesn't end
on newlines >==
```


# Built-in Functions

## STDIN

Standard input can be read from with `???`.
It will read until it receives a newline character.

`x: ???` will assign to `x` as a string what it reads from standard input, stopping at a newline character.

A prompt can be given by preceding the `???` with a string, for example `"input: "???`

## STDOUT

Objects can be written to standard output by appending a `!` character to them.
Note that they won't be written exactly as they would appear in Samarium:

`"a"!` will write `a` to standard output.

`//\/!` will write `13` to standard output.

## STDERR

Similarly to STDOUT, objects can be written to standard error using `!!!`.
This will throw an error, and exit the program if the error is not caught.

`"exception raised"!!!` will write `[Error] exception raised` to standard error.

## EXIT

The program may be exited with `=>!`.
If a particular exit code is desired, it may be put after the exclamation mark:

`=>!//` will exit the program with exit code 3.

## HASH

The hash function `##` returns as an integer the hash value of an object if it has one (arrays and tables do not).
The value it returns will remain consistent for the life of the program, but may vary if the program is run multiple times.

`"hash"##` will return the hash value of the string `"hash"`.

## TYPEOF

The typeof function `?!` returns the type of an object, as an instance of the `Type` class.

`/?!` returns `Integer`.

`"abc"?!` returns `String`.

`/?!?!` returns `Type`.


# Control Flow

## if/else

`if` statements are written using a `?` character, and `else` is written as `,,`.
Blocks are enclosed in curly brackets.
`else if` can be written using `,, ?`.

```
? x < \ {
    "x is negative"!;
} ,, ? x > / {
    "x is positive"!;
} ,, {
    "x = 0"!;
}
```


# Functions

Functions are defined using the `*` character.
Both the function's name and its parameters come before this `*` character, in that order, separated by spaces.
The function body is enclosed in curly brackets.
The function's return value is preceded by a `*` character as well.
(Functions may also have multiple return statements, or none at all.)

```
func arg1 arg2 * {
    sum: arg1 + arg2;
    * sum;
}
```

Calling a function is done as in C-like languages, with the function name, followed by its arguments in parentheses, separated by commas.

```
a: /;
b: /\;
c: func(a, b);      == using `func` from the previous example (c = 3)
```

## Main Function

The main function/entrypoint of the program is denoted by `=>`.
This function will be implicitly called on execution of the program.
The return value of the main function indicates the exit code of the program (optional, defaults to 0).
Attempts to write to stdout outside the scope of this or any other function will be ignored. 
Command line arguments can be gotten as an array with an optional parameter in this function.

```
=> argv * {
    == program here...
}
```

## Default Arguments

Default arguments may be given by using the assignment operator in the function definition.
Default arguments must come after any other arguments.

```
func a b c: "arg" d: _ * {
    == ...
}

func(/, /\);
func(/, /\, //);
func(/, /\, //, /\\);   == all valid calls
```
