# Variables

Variables are defined using the assignment operator `:`, like so:
```sm
my_var: /;
```
Variables can have many types, such as integers, strings, arrays, tables, and null.
Functions and classes may also be treated as first-class variables.
Only letters, numbers, and underscores can be used for variable names (case sensitive).

!!! note
    Samarium follows the same naming convention as Python, i.e.:
    - snake_case for variables and functions
    - PascalCase for classes and type aliases
    - flatcase for modules

Variables can be made private by prefixing the name with `#`, making them inaccessible to external modules. Private variable names don't collide with public variable names:
```sm
var: -/;
#var: /;

var!;  == -1
#var!;  == 1
```

## Main Function

The main function/entrypoint of the program is denoted by `=>`.
This function will be implicitly called on execution of the program.
The return value of the main function indicates the exit code of the program (optional, defaults to 0).
Attempts to write to stdout outside the scope of this or any other function will be ignored.
Command line arguments can be gotten as an array with an optional parameter in this function.

```sm
=> argv * {
    == program here
}
```
