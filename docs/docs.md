# Introduction

# Table of Contents
- [Introduction](#introduction)
- [Table of Contents](#table-of-contents)
- [Numbers](#numbers)
  - [Syntax](#syntax)
- [Operators](#operators)
  - [Arithmetic](#arithmetic)
  - [Comparison](#comparison)
  - [Logical and Membership](#logical-and-membership)
  - [Bitwise](#bitwise)
  - [Assignment](#assignment)

# Numbers
Numbers in Samarium are represented in base 2 using slashes and backslashes. Only integers are supported in Samarium.

## Syntax
Let's see some examples of Samarium numbers.

<center>

Base 10 | Base 2 | Samarium
---: | ---: | ---:
`0` | `0` | `\`
`1` | `1` | `/`
`2` | `10` | `/\`
`3` | `11` | `//`
`5` | `101` | `/\/`
`8` | `1000` | `/\\\`
`13` | `1101` | `//\/`
`21` | `10101` | `/\/\/`

</center>

Since Samarium is being transpiled to Python, there's no limit to how long an integer value can be.

```
//\\/\\//////\\\\///\\////\\/\\/\\\\\\/////\\\\\\\\/////\\//\\/\\////\\////////\\////\\///\\\\\\\\//\\\\//\\///\\/\\\\\\/\\////\\//\\\\/\\\\/\\////\\/////\\/\\\\/\\\\\\\\\\//\\\\\\//\\\\/\\/\\\\//\\\\\\///\\/\\\\\\/\\\\\\/\\\\///\\//\\\\/\\\\//\\\\///\\//\\\\\\\\\\\\////////////////////////////////////////////////////////////////////////////////
```
Or in base 10: 
```py
99999999999999999999999999999999999999999999999999999999999999999999999999999999
```

# Operators
Currently, samarium supports ? operators.

## Arithmetic

<center>

Operator | Meaning
--- | ---
`+` | Addition
`-` | Subtraction
`++` | Multiplication
`--` | Integer division
`+++` | Exponentiation
`---` | Modulus

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

Variables are defined using the `:` operator.
```
x : ///;
x + /!;
```
The code above is going to output `/\\\`.

Additionally, all arithmetic and bitwise (except `~`) operators can be used together with assignment to save some space.

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
