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

    => var * {
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
}
```


There are a number of special methods that the user can implement to override certain functionality of a class, such as how it's initialized (with the `create` method), or how it interacts with different operators.
These methods are as follows (where `func(...)` indicates a variable number of arguments):

<center>

Function                       | Python       | Use
---                            | ---          | ---
`+(other)`                     | `add`        | Interacts with the addition operator `+`.
`&(other)`                     | `and`        | Interacts with the bitwise AND operator `&`.
`()(...)`                      | `call`       | Called when an instance itself is "called" as a function;<br>`x(...)` roughly translates to `x?!.call(x, ...)`.
`%()`                          | --           | Interacts with the cast function character `%`.
`=>(...)`                      | `init`       | Initializes an instance of a class, takes any number<br>of arguments. Typically used for setting instance<br>variables based on these arguments.<br>No return value necessary.
`--(other)`                    | `floordiv`   | Interacts with the division operator `--`.
`::(other)`                    | `eq`         | Implements the equality operator `::`.
`<<>>(index)`                  | `getitem`    | Implements indexing an object;<br>`x<<index>>` is equivalent to `x.get_item(index)`.
`>(other)`                     | `gt`         | Implements the greater than operator `>`.
`>:(other)`                    | `ge`         | Implements the greater than or equal operator `>:`.
`->?(item)`                    | `contains`   | Implements membership testing,<br>returns `1` (object contains `item`)<br>or `0` (object does not contain `item`).<br>Interacts with `->?` operator.
`##()`                         | `hash`       | Called by the built-in hash function `##`,<br>and for keys in a table.<br>Objects which compare equal<br>should have the same hash value.
`...()`                        | `iter`       | Called when iterating over an object in a `foreach` loop.<br>Returns an array of objects to iterate over.
`<(other)`                     | `lt`         | Implements the less than operator `<`.
`<:(other)`                    | `le`         | Implements the less than or equal operator `<:`.
`---(other)`                   | `mod`        | Interacts with the modulo operator `---`.
`++(other)`                    | `mul`        | Interacts with the multiplication operator `++`.
`-_()`                         | `neg`        | Interacts with the negative unary operator `-`.
`~()`                          | `invert`     | Interacts with the bitwise NOT operator `~`.
`:::(other)`                   | `ne`         | Implements the inequality operator `:::`.
`|(other)`                     | `or`         | Interacts with the bitwise OR operator `\|`.
`+_()`                         | `pos`        | Interacts with the positive unary operator `+`.
`+++(other)`                   | `pow`        | Interacts with the exponentiation operator `+++`.
`<<>>:(index, value)`          | `setitem`    | Implements assigning to an index of an object;<br>`x<<index>>: value` is equivalent<br>to `x.set_item(index, value)`.
`$()`                          | --           | Interacts with the special function character `$`.
`-(other)`                     | `sub`        | Interacts with the subtraction operator `-`.
`?()`                          | `bool`       | Implements boolean value testing,<br>returns `1` (truthy) or `0` (falsy).<br>Used for conditional statements and logical operators.
`!()`                          | `str`        | Returns the string representation of an object.
`^(other)`                     | `xor`        | Interacts with the bitwise XOR operator `^`.

</center>

Two special methods – `=>` and `!` – have default definitions:
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
    => * {}

    ! * {
        * "<$name@$address>" --- {{"name" -> '?!, "address" -> '**}};
    }
}
```

Some of the comparison operators can be inferred from others,
so not all of them are necessary to provide implementations for.
The following operators infer from each other:
- `::` and `:::`
- `>` and `<`
- `>:` and `<:`


## Static Methods
Methods can be made static by replacing the `*` keyword with the `~'*` keyword
(where `~'` can be read as "no instance"):
```sm
<=calendar.date;

@ Calendar {
    is_weekend date ~'* {
        * date.weekday > /\\;
    }
}

=> * {
    Calendar.is_weekend(date("2022-11-08"))!;  == 0
}
```


## Classes As Entry Points

A class named `=>` can serve as an entry point instead of a function:
```sm
=> argv * {
    "Hello, " + argv<</>>!;
}
```
```sm
@ => {
    => argv * {
        "Hello, " + argv<</>>!;
    }
}
```


## Class Decorators

Decorators can also be created using classes:
```sm
@ OutputStorage {

    => func * {
        'func: func;
        'outputs: [];
    }

    () args... * {
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
