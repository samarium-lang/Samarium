# Classes

Classes are defined with the `@` character.
Any inherited classes can follow the name of the class in parentheses, separated by commas[^1].
Class variables and methods are defined inside curly braces.

Inside a class' methods, the `'` character can be used to reference its instance variables and methods.
Class variables are those that are shared between all instances of a class, and instance variables are for data unique to each instance.

Class variables, instance variables and methods can be accessed with the `.` operator on an instance of the class.
In this case, class methods will implicitly be given a reference to the instance as the first argument of the method; `x.method(arg1, arg2, ...)` is equivalent to `x?!.method(x, arg1, arg2, ...)`.
Class variables and methods can also be accessed in the same way directly from the class itself, though note that in this case methods will not implicitly have an instance as the first argument, so it must be provided.

<<<<<<< HEAD:docs/classes.md
=======

>>>>>>> master:docs/12classes.md
```sm
@ A {
    shared: [];         == class variable

    create var * {
        'var: var;
    }

    method arg * {      == method definition
        'var: /;        == instance variable
        * 'var;         == return value
    }
}

=> * {
    a: A(/\\);          == calls `A.create(4)`; `a` is now an instance of `A`
    a.method(/\/);      == calls `A.method` on the instance `a` with `arg` 5
<<<<<<< HEAD:docs/classes.md
    a.var!;             == prints 5
=======
    a.var;              == prints 5
>>>>>>> master:docs/12classes.md

    b: A(/\);
    a.shared+: ["str"]; == modifying a class variable for all instances
    b.shared!;          == prints ["str"]
}
```

Parent classes are inherited from right to left, i.e. the first class in the inheritance takes priority and will overwrite any functions/variables defined by the following classes:

<<<<<<< HEAD:docs/classes.md
=======

>>>>>>> master:docs/12classes.md
```sm
@ A {
    method * { "A"!; }
}

@ B {
    method * { "B"!; }
}

@ C(A, B) {
<<<<<<< HEAD:docs/classes.md
    create * {}
=======
    create * { }
>>>>>>> master:docs/12classes.md
}

=> * {
    c: C();
<<<<<<< HEAD:docs/classes.md
    c.method();     == prints "A", as class A was inherited last
}
```
=======
    c.method();     == prints "A", as class `A` was inherited last
}
```

>>>>>>> master:docs/12classes.md

There are a number of special methods that the user can implement to override certain functionality of a class, such as how it's initialized (with the `create` method), or how it interacts with different operators.
These methods are as follows (where `func(...)` indicates a variable number of arguments):

Function                    | Python       | Use
---                         | ---          | ---
`create(...)`               | `init`       | Initializes an instance of a class, takes any number of arguments. Typically used for setting instance variables based on these arguments. No return value necessary.
`toString()`                | `str`        | Returns the string representation of an object.
`toBit()`                   | `bool`       | Implements boolean value testing, returns `1` (truthy) or `0` (falsy). Used for conditional statements and logical operators.
`has(item)`                 | `contains`   | Implements membership testing, returns `1` (object contains `item`) or `0` (object does not contain `item`). Interacts with `->?` operator.
`call(...)`                 | `call`       | Called when an instance itself is "called" as a function; `x(...)` roughly translates to `x?!.call(x, ...)`.
`hash()`                    | `hash`       | Called by the built-in hash function `##`, and for keys in a table. Objects which compare equal should have the same hash value.
`iterate()`                 | `iter`       | Called when iterating over an object in a `foreach` loop. Returns an array of objects to iterate over.
`subtract(other)`           | `sub`        | Interacts with the subtraction operator `-`. `x - y` is equivalent to `x.subtract(y)`.
`subtractAssign(other)`     | `isub`       | Interacts with the subtraction assignment operator `-:`. `x-: y` is equivalent to `x.subtractAssign(y)` (or `x: x - y`).
`add(other)`                | `add`        | Interacts with the addition operator `+`.
`addAssign(other)`          | `iadd`       | Interacts with the addition assignment operator `+:`.
`multiply(other)`           | `mul`        | Interacts with the multiplication operator `++`.
`multiplyAssign(other)`     | `imul`       | Interacts with the multiplication assignment operator `++:`.
`divide(other)`             | `floordiv`   | Interacts with the division operator `--`.
`divideAssign(other)`       | `ifloordiv`  | Interacts with the division assignment operator `--:`.
`mod(other)`                | `mod`        | Interacts with the modulo operator `---`.
`modAssign(other)`          | `imod`       | Interacts with the modulo assignment operator `---:`.
`power(other)`              | `pow`        | Interacts with the exponentiation operator `+++`.
`powerAssign(other)`        | `ipow`       | Interacts with the exponentiation assignment operator `+++:`.
`and(other)`                | `and`        | Interacts with the bitwise AND operator `&`.
`andAssign(other)`          | `iand`       | Interacts with the bitwise AND assignment operator `&:`.
`or(other)`                 | `or`         | Interacts with the bitwise OR operator `\|`.
`orAssign(other)`           | `ior`        | Interacts with the bitwise OR assignment operator `\|:`.
`xor(other)`                | `xor`        | Interacts with the bitwise XOR operator `^`.
`xorAssign(other)`          | `ixor`       | Interacts with the bitwise XOR assignment operator `^:`.
`negative()`                | `neg`        | Interacts with the negative unary operator `-`.
`positive()`                | `pos`        | Interacts with the positive unary operator `+`.
`not()`                     | `invert`     | Interacts with the bitwise NOT operator `~`.
`getItem(index)`            | `getitem`    | Implements indexing an object; `x<<index>>` is equivalent to `x.getItem(index)`.
`setItem(index, value)`     | `setitem`    | Implements assigning to an index of an object; `x<<index>>: value` is equivalent to `x.setItem(index, value)`.
`equals(other)`             | `eq`         | Implements the equality operator `::`. `x :: y` is equivalent to `x.equals(y)`.
`notEquals(other)`          | `ne`         | Implements the inequality operator `:::`.
`lessThan(other)`           | `lt`         | Implements the less than operator `<`.
`greaterThan(other)`        | `gt`         | Implements the greater than operator `>`.
`lessThanOrEqual(other)`    | `le`         | Implements the less than or equal operator `<:`.
`greaterThanOrEqual(other)` | `ge`         | Implements the greater than or equal operator `>:`.
`special()`                 | --           | Interacts with the special function character `$`.
`cast()`                    | --           | Interacts with the cast function character `%`.

Note: Some of the comparison operators can be inferred from others, so not all of them are necessary to provide implementations for.
The specific operators needed to infer each comparison operator are listed in the following table:

Operator | Inferred from
---      | ---
`:::`    | `::`
`<`      | `>` and `::`
`<:`     | `>`
`>:`     | `>` and `::`

<<<<<<< HEAD:docs/classes.md
<sup id="note-a">a</sup> Note that order will be preserved here — if both class `A` and class `B` implement a function `f`, and class `C` inherits them in the order `(A, B)`, then `C` will inherit `f` from class `B`, as it is inherited later.

## Class Decorators
Decorators can also be created using classes:
```sm
@ OutputStorage {

    create func * {
        'func: func;
        'outputs: [];
    }

    call args... * {
        out: 'function(**args);
        'outputs_: [out];
        * out;
    }

}

OutputStorage @ multiply a b * {
    * a ++ b;
}

multiply(/\, /\/)!;  == 10
multiply(//, ///)!;  == 21
multiply(/\\/, //\\)!;  == 108

multiply.outputs!;  == [10, 21, 108]
```
=======
[^1]: Note that order will be preserved here — if both class `A` and class `B` implement a function `f`, and class `C` inherits them in the order `(A, B)`, then `C` will inherit `f` from class `B`, as it is inherited later.
>>>>>>> master:docs/12classes.md
