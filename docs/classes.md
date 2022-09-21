# Classes

Classes are defined with the `@` character.
Any inherited classes can follow the name of the class in parentheses, separated by commas[^1].
Class variables and methods are defined inside curly braces.

Inside a class' methods, the `'` character can be used to reference its instance variables and methods.
Class variables are those that are shared between all instances of a class, and instance variables are for data unique to each instance.

Class variables, instance variables and methods can be accessed with the `.` operator on an instance of the class.
In this case, class methods will implicitly be given a reference to the instance as the first argument of the method; `x.method(arg1, arg2, ...)` is equivalent to `x?!.method(x, arg1, arg2, ...)`.
Class variables and methods can also be accessed in the same way directly from the class itself, though note that in this case methods will not implicitly have an instance as the first argument, so it must be provided.

Just like variables, class attributes can be made private by prefixing them with `#`, making them inaccessible outside the class.

```sm
@ Foo {
    shared: [];

    create var * {
        'var: var;
        '#pv: var - /;
    }

    get_pv * {
        * '#pv;
    }
}

=> * {
    a: Foo(/\\);        == calls `Foo.create`; `a` is now an instance of `Foo`
    a.var!;             == prints 5
    a.get_pv()!;        == calls `Foo.get_pv(a)`; prints 4

    b: Foo(/\);
    a.shared+: ["str"]; == modifying a class variable for all instances
    b.shared!;          == prints ["str"]
}
```

Parent classes are inherited from right to left, i.e. the first class in the inheritance takes priority and will overwrite any functions/variables defined by the following classes:

```sm
@ A {
    method * { "A"!; }
}

@ B {
    method * { "B"!; }
}

@ C(A, B) {}

=> * {
    c: C();
    c.method();     == prints "A", as class A was inherited last
```


There are a number of special methods that the user can implement to override certain functionality of a class, such as how it's initialized (with the `create` method), or how it interacts with different operators.
These methods are as follows (where `func(...)` indicates a variable number of arguments):

<center>

Function                       | Python       | Use
---                            | ---          | ---
`add(other)`                   | `add`        | Interacts with the addition operator `+`.
`add_assign(other)`            | `iadd`       | Interacts with the addition assignment operator `+:`.<br>`x+: y` is equivalent to `x.add_assign(y)` (or `x: x + y`).
`and(other)`                   | `and`        | Interacts with the bitwise AND operator `&`.
`and_assign(other)`            | `iand`       | Interacts with the bitwise AND assignment operator `&:`.
`call(...)`                    | `call`       | Called when an instance itself is "called" as a function;<br>`x(...)` roughly translates to `x?!.call(x, ...)`.
`cast()`                       | --           | Interacts with the cast function character `%`.
`create(...)`                  | `init`       | Initializes an instance of a class, takes any number<br>of arguments. Typically used for setting instance<br>variables based on these arguments.<br>No return value necessary.
`divide(other)`                | `floordiv`   | Interacts with the division operator `--`.
`divide_assign(other)`         | `ifloordiv`  | Interacts with the division assignment operator `--:`.
`equals(other)`                | `eq`         | Implements the equality operator `::`.
`get_item(index)`              | `getitem`    | Implements indexing an object;<br>`x<<index>>` is equivalent to `x.get_item(index)`.
`greater_than(other)`          | `gt`         | Implements the greater than operator `>`.
`greater_than_or_equal(other)` | `ge`         | Implements the greater than or equal operator `>:`.
`has(item)`                    | `contains`   | Implements membership testing,<br>returns `1` (object contains `item`)<br>or `0` (object does not contain `item`).<br>Interacts with `->?` operator.
`hash()`                       | `hash`       | Called by the built-in hash function `##`,<br>and for keys in a table.<br>Objects which compare equal<br>should have the same hash value.
`iterate()`                    | `iter`       | Called when iterating over an object in a `foreach` loop.<br>Returns an array of objects to iterate over.
`less_than(other)`             | `lt`         | Implements the less than operator `<`.
`less_than_or_equal(other)`    | `le`         | Implements the less than or equal operator `<:`.
`mod(other)`                   | `mod`        | Interacts with the modulo operator `---`.
`mod_assign(other)`            | `imod`       | Interacts with the modulo assignment operator `---:`.
`multiply(other)`              | `mul`        | Interacts with the multiplication operator `++`.
`multiply_assign(other)`       | `imul`       | Interacts with the multiplication<br>assignment operator `++:`.
`negative()`                   | `neg`        | Interacts with the negative unary operator `-`.
`not()`                        | `invert`     | Interacts with the bitwise NOT operator `~`.
`not_equals(other)`            | `ne`         | Implements the inequality operator `:::`.
`or(other)`                    | `or`         | Interacts with the bitwise OR operator `\|`.
`or_assign(other)`             | `ior`        | Interacts with the bitwise OR assignment operator `\|:`.
`positive()`                   | `pos`        | Interacts with the positive unary operator `+`.
`power(other)`                 | `pow`        | Interacts with the exponentiation operator `+++`.
`power_assign(other)`          | `ipow`       | Interacts with the exponentiation<br>assignment operator `+++:`.
`set_item(index, value)`       | `setitem`    | Implements assigning to an index of an object;<br>`x<<index>>: value` is equivalent<br>to `x.set_item(index, value)`.
`special()`                    | --           | Interacts with the special function character `$`.
`subtract(other)`              | `sub`        | Interacts with the subtraction operator `-`.
`subtract_assign(other)`       | `isub`       | Interacts with the subtraction assignment operator `-:`.
`to_bit()`                     | `bool`       | Implements boolean value testing,<br>returns `1` (truthy) or `0` (falsy).<br>Used for conditional statements and logical operators.
`to_string()`                  | `str`        | Returns the string representation of an object.
`xor(other)`                   | `xor`        | Interacts with the bitwise XOR operator `^`.
`xor_assign(other)`            | `ixor`       | Interacts with the bitwise XOR assignment operator `^:`.

</center>

Two special methods – `create` and `to_string` – have default definitions:
```sm
@ Foo {}

=> * {
    f: Foo();
    f!;  == <Foo@7fe5403d7b00>
}
```
The above class definition is equivalent to:
```sm
@ Foo {
    create * {}

    to_string * {
        <-string.format;
        * format("<$name@$address>", {{"name" -> '?!, "address" -> '**}});
    }
}
```

Some of the comparison operators can be inferred from others, so not all of them are necessary to provide implementations for.
The specific operators needed to infer each comparison operator are listed in the following table:

Operator | Inferred from
---      | ---
`:::`    | `::`
`<`      | `>` and `::`
`<:`     | `>`
`>:`     | `>` and `::`


## Classes As Entry Points

A class named `=>` can serve as an entry point instead of a function:
```sm
=> argv * {
    "Hello, " + argv<</>>!;
}
```
```sm
@ => {
    create argv * {
        "Hello, " + argv<</>>!;
    }
}
```


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

[^1]: Note that order will be preserved here — if both class `A` and class `B` implement a function `f`, and class `C` inherits them in the order `(A, B)`, then `C` will inherit `f` from class `A`, as it is inherited later.
