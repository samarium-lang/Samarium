<style>
h1, h2, h3 {
    text-align: center;
    font-weight: bold;
}
</style>

- [About](#about)
  - [To-Do:](#to-do)
  - [File Extension: `.sm`](#file-extension-sm)
  - [Chars used: `+-><:.,&|=~;!?"'[]{}\/*@#$%^()`](#chars-used--)
  - [Free chars: `_`](#free-chars-_)
  - [Supported types](#supported-types)
    - [Vector (`[]`)](#vector-)
    - [Integer (`/\`)](#integer-)
    - [Subroutine (`*`)](#subroutine-)
    - [Class (`@`)](#class-)
- [Instructions](#instructions)
  - [Comments](#comments)
  - [Importing](#importing)
  - [Try Catch](#try-catch)
  - [Anonymous Function](#anonymous-function)
  - [Constants](#constants)
  - [Subroutine / Function](#subroutine--function)
  - [Class](#class)
  - [Arithmetic](#arithmetic)
  - [Comparison](#comparison)
  - [Logical and Bitwise](#logical-and-bitwise)

# About

## To-Do:
- Map (`{}`?)
- Exception names

## File Extension: `.sm`

## Chars used: `+-><:.,&|=~;!?"'[]{}\/*@#$%^()`
## Free chars: `_`

## Supported types
### Vector (`[]`)
### Integer (`/\`)
### Subroutine (`*`)
### Class (`@`)

# Instructions

## Comments
```
== this is a single line comment

==<this
is a
multiline
comment>==
```

## Importing
```
$math;
```
```py
import math
```

## Try Catch
```
?? {
    / -- \!;
} !! {
    \!;
}
```
```py
try:
    print(1 / 0)
except:
    print(0)
```

## Anonymous Function
```
prod : * _ a b {* a ++ b;};
```
```py
prod = lambda a, b: a * b
```

## Constants
```
# piFloored : //;
pi : /\; == SyntaxError
```

## Subroutine / Function
```
%debug
* name arg1 arg2 {
    arg1!;
    arg2!;
    * arg1 + arg2;
}
```
```py
def name(arg1, arg2):
    print(arg1)
    print(arg2)
    return arg1 + arg2
```

## Class
```
@ Person {
    * init name age {
        ins.name : name;
        ins.age : age ++ //\\;
    }

    * show {
        "$name is $age months old"!;
    }
}

person : Person("John", 20);
person.show();
```
```py
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age * 12
    
    def show(self):
        print(f"{self.name} is {self.age} months old")

person = Person("John", 20)
person.show()
```

## Arithmetic

<center>

Operator | Description
:---: | :---:
`+` | ADD, e.g. `30 + 13` is `43`
`-` | SUB, e.g. `30 - 13` is `17`
`++` | MUL, e.g. `30 ++ 13` is `390`
`--` | DIV, e.g. `30 -- 13` is `2`
`+++` | POW, e.g. `30 +++ 13` is `1.594323e19`
`---` | MOD, e.g. `30 --- 13` is `4`

</center>

## Comparison

<center>

Operator | Description
:---: | :---:
`>` | GT, e.g. `/ > \ :: /`
`<` | LT, e.g. `/ < \ :: \`
`>:` | GE, e.g. `/ >: / :: /`
`<:` | LE, e.g. `\ <: / :: /`
`::` | EQ, e.g. `(/ :: /) :: /`
`:::` | NE, e.g. `(/ -:: /) :: \`

</center>

## Logical and Bitwise

<center>

Operator | Description
:---: | :---:
`&` | AND, e.g. `/ & \ :: \`
`\|` | OR, e.g. `/ \| \ :: /`
`^` | XOR, e.g. `/ ^ / :: \`
`~` | NOT, e.g. `~/ :: \`

</center>