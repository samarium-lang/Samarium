# Variables

Variables are defined using the assignment operator `:`, like so:

```sm
myVar: /;
```

Variables can have many types, such as integers, strings, arrays, tables, and null.
Functions and classes may also be treated as first-class variables.
Only letters and/or numbers can be used for variable names (case sensitive), thus camelCase is recommended for names consisting of multiple words.

!!! note
    Statements in Samarium must end in a semicolon. Also, backticks are ignored.

## Null

The character `_` represents a null value, such as for default arguments in a function.
Assignments to `_` are not allowed.

## Constants

Variables can be made constant by prefixing them with `<>`.
Any attempt to assign a new value to a constant variable will raise a `TypeError`.

```sm
<>x: //;
x: \;
```

This example raises `[TypeError] object is immutable`.
