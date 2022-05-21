# Variables

Variables are defined using the assignment operator `:`, like so:
```sm
myVar: /;
```
Variables can have many types, such as integers, strings, arrays, tables, and null.
Functions and classes may also be treated as first-class variables.
Only letters and/or numbers can be used for variable names (case sensitive), thus camelCase is recommended for names consisting of multiple words.

## Null

The character `_` represents a null value, such as for default arguments in a function.
Assignments to `_` are not allowed.