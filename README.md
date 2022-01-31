# Samarium

Samarium is a dynamic interpreted language transpiled to Python.
Samarium, in its most basic form, doesn't use any digits or letters.

Here's a `Hello, World!` program written in Samarium:
```rs
=> * {
  "Hello, World!"!;
}
```

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
- [Comments](#comments)
- [Built-in functions](#built-in-functions)
- [Control flow](#control-flow)
- [Functions](#functions)
- [Importing](#importing)
- [Classes](#classes)
- [Standard Library](#standard-library)


# Variables

Variables are defined using the assignment operator `:`, like so:
```rs
myVar: /;
```
Variables may be integers, strings, arrays, tables, or null.
Only letters can be used for variable names, thus camelCase is recommended for names consisting of multiple words.

## Null

The character `_` represents a null value, such as for default arguments in a function.
Assignments to `_` are not allowed.


# Numbers

Numbers are represented in base 2, using slashes and backslashes to represent 1 and 0 respectively.
Only integers are supported in Samarium.

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

```hs
//\\/\\//////\\\\///\\////\\/\\/\\\\\\/////\\\\\\\\/////\\//\\/\\////\\////////\\////\\///\\\\\\\\//\\\\//\\///\\/\\\\\\/\\////\\//\\\\/\\\\/\\////\\/////\\/\\\\/\\\\\\\\\\//\\\\\\//\\\\/\\/\\\\//\\\\\\///\\/\\\\\\/\\\\\\/\\\\///\\//\\\\/\\\\//\\\\///\\//\\\\\\\\\\\\////////////////////////////////////////////////////////////////////////////////
```
Or in base 10: 
```py
99999999999999999999999999999999999999999999999999999999999999999999999999999999
```


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
```rs
[\, \/, \\]
```

Arrays can be concatenated with the `+` operator:

`[/, //] + [/\]` is the same as `[/, //, /\]`

Elements can also be removed from an array using the `-` operator:

`[/, //\, /\, //] - //\` gives `[/, /\, //]`


# Tables

Tables are defined using double curly braces:
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
`<<index>>`             | the element at index `index`
`<<..stop>>`            | all elements up to index `stop`
`<<**step>>`            | all elements separated by gaps of size `step`
`<<start..>>`           | all elements starting from index `start`
`<<..stop**step>>`      | all elements up to index `stop` separated by gaps of size `step`
`<<start**step>>`       | all elements starting from index `start` separated by gaps of size `step`
`<<start..stop>>`       | all elements starting from index `start` up to index `stop`
`<<start..stop**step>>` | all elements starting from index `start` up to index `stop` separated by gaps of size `step`


# Comments

Comments are written using `==`, and comment blocks are written with `==<` and `>==`:
```hs
== single-line comment

==< comment block
doesn't end
on newlines >==
```


# Built-in functions

## STDIN

Standard input can be read from with `???`.
It will read until it receives a newline character.

`x: ???` will assign to `x` as a string what it reads from standard input, stopping at a newline character.

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
