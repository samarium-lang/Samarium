# Introduction

Samarium is a dynamic language transpiled to Python. Samarium in its most basic form, doesn't use any digits or letters.

Here's a `Hello, World!` program written in Samarium:
```rs
"Hello, World!"!;
```

The following guide assumes that you are familiar with the basics of programming.

# Table of Contents
- [Introduction](#introduction)
- [Table of Contents](#table-of-contents)
- [Strings](#strings)
  - [Operations on Strings](#operations-on-strings)
- [Numbers](#numbers)
  - [Syntax](#syntax)
- [Creating Variables](#creating-variables)
- [Operators](#operators)
  - [Arithmetic](#arithmetic)
  - [Comparison](#comparison)
  - [Logical and Membership](#logical-and-membership)
  - [Bitwise](#bitwise)
  - [Assignment](#assignment)

# Strings
Strings in Samarium are defined using double quotation marks, as shown in the introductory example:
```rs
"Hello!"
```
Multiline strings do not require any additional syntax, you simply do:
```rs
"This
is a
multiline
string"
```
## Operations on Strings
<!-- todo: concatenation with +, cloning with ++,  -->

# Numbers
Numbers in Samarium are represented in base 2 using slashes and backslashes. Only integers are supported in Samarium.

## Syntax
Let's see some examples of Samarium numbers.

<center>

Base 10 | Base 2  | Samarium
---:    | ---:    | ---:
`0`     | `0`     | `\`
`1`     | `1`     | `/`
`2`     | `10`    | `/\`
`3`     | `11`    | `//`
`5`     | `101`   | `/\/`
`8`     | `1000`  | `/\\\`
`13`    | `1101`  | `//\/`
`21`    | `10101` | `/\/\/`

</center>

Since Samarium is being transpiled to Python, there's no limit to how long an integer value can be.

```
//\\/\\//////\\\\///\\////\\/\\/\\\\\\/////\\\\\\\\/////\\//\\/\\////\\////////\\////\\///\\\\\\\\//\\\\//\\///\\/\\\\\\/\\////\\//\\\\/\\\\/\\////\\/////\\/\\\\/\\\\\\\\\\//\\\\\\//\\\\/\\/\\\\//\\\\\\///\\/\\\\\\/\\\\\\/\\\\///\\//\\\\/\\\\//\\\\///\\//\\\\\\\\\\\\////////////////////////////////////////////////////////////////////////////////
```
Or in base 10: 
```py
99999999999999999999999999999999999999999999999999999999999999999999999999999999
```

# Creating Variables

Samarium variables are defined using the colon `:` operator.
```bash
myNumber : /\/;
myString : "I'm a teapot";
```
Only letters can be used for variable names, thus camelCase is recommended for names consisting of multiple words.

# Operators
Currently, Samarium supports 34 operators.

## Arithmetic

<center>

Operator | Meaning
--- | ---
`+` | Addition
`-` | Subtraction
`++` | Multiplication
`--` | Integer division
`+++` | Exponentiation
`---` | Modulo

</center>

## Comparison

<center>

Operator | Meaning
--- | ---
`<` | Less than
`>` | Greater than
`<:` | Less than or equal to
`>:` | Greater than or equal to
`::` | Equal to
`:::` | Not equal to

</center>

## Logical and Membership

<center>

Operator | Meaning
--- | ---
`&&` | Logical AND
`\|\|` | Logical OR
`~~` | Logical NOT
`->?` | Returns `/` when `x` is a part of `y` in `x ->? y`

</center>

## Bitwise

<center>

Operator | Meaning
--- | ---
`&` | Bitwise AND
`\|` | Bitwise OR
`^` | Bitwise XOR
`~` | Bitwise NOT
`<<` | Left shift
`>>` | Right shift

</center>

## Assignment

All arithmetic and bitwise (except `~`) operators can be used together with the assignment operator `:` to save some space.

So instead of
```
x : //\/;
x : x ++ //;
x : x --- /\\;
x : x << /\;
x!;
```
one could do
```
x : //\/;
x ++: //;
x ---: /\\;
x <<: /\;
x!;
```
