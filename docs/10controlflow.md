# Control Flow

## `if`/`else`

`if` statements are written using a `?` character, and `else` is written as `,,`.
Blocks are enclosed in curly brackets.
`else if` can be written using `,, ?`.

```sm
? x < \ {
    "x is negative"!;
} ,, ? x > \ {
    "x is positive"!;
} ,, {
    "x = 0"!;
}
```

## `foreach` loop

`foreach` loops are written using `...`, and enclosed in curly brackets.
Each of these loops must be paired with a `->?` operator, indicating the object to iterate over.

```sm
arr: [];
... char ->? "string" {
    arr+: [char];
}
== arr :: ["s", "t", "r", "i", "n", "g"]
```

## `while` loop

`while` loops are written with `..`, and enclosed in curly brackets.
The loop condition follows the `..`.
An infinite loop is created when no condition is given.

```sm
x: \;
.. x < /\/\ {
    x+: /\;
    x!;
}
== prints 2, 4, 6, 8, 10
```

## `break`/`continue`

`break` statements are written with `<-`, and terminate the enclosing loop immediately.
They can be used in both `for` and `while` loops.

```sm
x: \;
.. x < /\/ {
    x+: /;
    ? x :: // {
        <-;
    }
    x!;
}
```

This program will print 1, 2, and then terminate the `while` loop on the third iteration, before printing 3.

`continue` statements are written with `->`, and immediately finish the current iteration of the enclosing loop.
These can also be used in both `for` and `while` loops.

```sm
x: \;
.. x < /\/ {
    x+: /;
    ? x :: // {
        ->;
    }
    x!;
}
```

This program will print 1, 2, skip the third iteration of the `while` loop, then print 4, 5, and end the loop normally.

## `try`/`catch`

`try`-`catch` statements are used for error handling.
`try` clauses are written with `??`, and enclosed in curly brackets.
If, during execution of the contents of the `try` clause, an error is thrown, the rest of the clause is skipped, the error will be silenced, and the adjoining `catch` clause will be executed.
`catch` clauses are written with `!!`, and are also enclosed in curly brackets.

```sm
?? {
    == error prone code here...
    / -- \;
    "unreachable"!;
} !! {
    "error caught"!;
}
```