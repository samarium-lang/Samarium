# Modules

Modules can contain functions and variables that a user may wish to import.
Modules are named after their filename (with `.sm` omitted).
Like variables, module names must consist of only letters and numbers, and are case sensitive.


## Importing

Modules can be imported using the `<-` operator, followed by the module's name.
Objects (classes, functions, variables) from this module can then be accessed with the `.` operator.
Module objects are always truthy.

```sm
<=string;
== imports the `string` module from Samarium's standard library

string.to_upper("abc")!;
== prints "ABC"

string.digits!;
== prints "0123456789"
```

Objects can also be directly imported from a module one by one, in which case they don't need to be preceded by the module name when using them:

```sm
<=math.[abs, sqrt];

sqrt(/\\/)!;    == prints 3
abs(-/\)!;      == prints 2
```

All objects in a module can be directly imported at once by using the wildcard character `*`.
Importing everything in this way is typically advised against, as it may cause poorly readable code and/or name collisions.

```sm
<=math.*;

factorial(//)!;     == prints 6
```


### Import Aliases

Imported objects can be renamed if needed by using the `name -> new_name` syntax:
```sm
<=string.[to_upper -> shout, strip];

str: " hello! ";
shout(strip(str))!;  == HELLO!
```
This is different to
```
<=string.to_upper;

shout: to_upper;
```
because in this case, both `to_upper` and `shout` are valid options,
whereas the first code block only has `shout`.


### Inline Imports

Imports that are going to be only used once can be replaced
by inline imports (using the `<-` keyword):
```sm
=> * {
    i: /?!("Enter a number: "???);
    ? <-math.is_prime(i) {
        i, "is a prime number"!;
    }
}
```