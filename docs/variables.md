# Variables

Variables are defined using the assignment operator `:`, like so:
```sm
my_var: /;
```
Variables can have many types, such as integers, strings, arrays, tables,
slices, or null. Functions and classes may also be treated as first-class
variables. Only letters, numbers, and underscores can be used
for variable names (case sensitive).

!!! note
    Samarium follows the same naming convention as Python, i.e.:<br>
    — snake_case for variables and functions<br>
    — PascalCase for classes and type aliases<br>
    — flatcase for modules

Variables can be made private by prefixing the name with `#`, making them
inaccessible to external modules. Private variable names don't collide with
public variable names:
```sm
var: -/;
#var: /;

var!;  == -1
#var!;  == 1
```
