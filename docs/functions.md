# Functions

Functions are defined using the `*` character.
Both the function's name and its parameters come before this `*` character, in that order, separated by spaces.
The function body is enclosed in curly brackets.
The function's return value is preceded by a `*` character as well.
(Functions may also have multiple return statements, or none at all.)

```sm
add a b * {
    sum: a + b;
    * sum;
}
```

Calling a function is done as in C-like languages, with the function name, followed by its arguments in parentheses, separated by commas.

```sm
a: /;
b: /\;
c: add(a, b);
```


## Optional Parameters

Parameters can be made optional by adding a `?` character after the parameter's name. Optional parameters are required to have a default value defined in the function's body using the `param <> default` syntax.

```sm
== string.leftpad
leftpad string length char? * {
    char <> " ";
    * pad(string, length, char) + string;
}

leftpad("hello", /\/\)!; ==      hello
leftpad("hello", /\/\, "-")!; == -----hello
```


## Varargs

A function can accept a variable number of arguments by adding `...` after the last parameter's name. Packed arguments will be passed into the function as an array.

```sm
product nums... * {
    prod: /;
    ... n ->? nums {
        prod++: n;
    }
    * prod;
}

prod()!; == 1
prod(///)!; == 7
prod(///, /\/\/)!; == 147
prod(/\/, /\\\/\, /\, /\\/\\\, ///)!; == 171360
```


## Argument Unpacking

Arguments can be spread into a function by using the `**` unary operator:

```sm
pow a b * {
    * a +++ b;
}

arguments = [/\, //];

pow(**arguments)!;
== equivalent to pow(/\, //)!;
```


## Decorators

Decorators are syntactic sugar for calling a function/class which argument is another callable.

To use a function as a decorator, write the name, `@` and then declare the function it is decorating.

```sm
== Decorator
double func * {
    wrapper args... * {
        * func(**args) ++ /\;
    }
    * wrapper;
}

== Decorated functions
double @ multiply a b * {
    * a ++ b;
}

double @ code_to_char code * {
    * code%;
}

multiply(/\, /\\)!;  == 16
code_to_char(/\\\\/)!;  == !!
```
