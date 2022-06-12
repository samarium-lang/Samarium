# Modules

Modules can contain functions and variables that a user may wish to import.
Modules are named after their filename (with `.sm` omitted).
Like variables, module names must consist of only letters and numbers, and are case sensitive.

## Importing

Modules can be imported using the `<-` operator, followed by the module's name.
Objects (classes, functions, variables) from this module can then be accessed with the `.` operator.

```sm
<-string;
== imports the `string` module from Samarium's standard library

string.toUpper("abc")!;
== prints "ABC"

string.digits!;
== prints "0123456789"
```

Objects can also be directly imported from a module one by one, in which case they don't need to be preceded by the module name when using them:

```sm
<<<<<<< HEAD:docs/modules.md
<-math.abs, sqrt;
=======
<-math.sqrt, abs;
>>>>>>> master:docs/11modules.md

sqrt(/\\/)!;    == prints 3
abs(-/\)!;      == prints 2
```

All objects in a module can be directly imported at once by using the wildcard character `*`.
Importing everything in this way is typically advised against, as it may cause poorly readable code and/or name collisions.

```sm
<-math.*;

<<<<<<< HEAD:docs/modules.md
factorial(//)!;     == prints 6
```
=======
factorial(//)!; == prints 6
```
>>>>>>> master:docs/11modules.md
