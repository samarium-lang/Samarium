# Functions

Functions are defined using the `*` character.
Both the function's name and its parameters come before this `*` character, in
that order, separated by spaces.
The function body is enclosed in curly brackets.
The function's return value is preceded by a `*` character as well.
(Functions may also have multiple return statements, or none at all.)

```sm
add a b * {
    sum: a + b;
    * sum;
}
```

Calling a function is done as in C-like languages, with the function name,
followed by its arguments in parentheses, separated by commas.

```sm
a: /;
b: /\;
c: add(a, b);
```

If no value is returned, the semicolon after `*` may be omitted:

```sm
exit code * {
    ? code {*}
    "Success"!;
}
```

## Main Function

The main function/entrypoint of the program is denoted by `=>`.
This function will be implicitly called on execution of the program.
The return value of the main function indicates the exit code of the program
(optional, defaults to 0). This function will not be called when importing
the module it's located in. Command line arguments can be gotten as an array
with an optional parameter in this function.

```sm
=> argv * {
    == program here
}
```


## Optional Parameters

Parameters can be made optional by adding a `?` character after the parameter's
name. Optional parameters are required to have a default value defined in the
function's body using the `param <> default` syntax.

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

A function can accept a variable number of arguments by adding `...` after the
last parameter's name. Packed arguments will be passed into the function as an
array.

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

Decorators are syntactic sugar for calling a function/class which argument is
another callable.

To use a function as a decorator, write the name, `@` and then declare the
function it is decorating.

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


## Iterators

Functions can yield values instead of returning them, thus making the function
behave like an iterator. Values are yielded with the `**` operator:

```sm
<=math.is_prime;

prime_generator * {
    x: /\;
    .. {
        ? is_prime(x) {
            ** x;
        }
        x+: /;
    }
}

pg: prime_generator();
pg!;
"Primes below 100:"!;
... i ->? pg {
    ? i > /\/\ +++ /\ {
        !;
        <-
    }
    ""?!(i) + " " ~> /;
}
```
```
<Iterator@7fd890475860>
Primes below 100:
2 3 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97
```

Just like with `*`, the semicolon after `**` can be omitted if no value is
yielded:
```sm
foo * {**}

[]?!(foo())!  == [null]
```

Iterators support special `$` and cast `%` methods.

`Iterator%` returns the length of the iterator if available, and null otherwise.

`Iterator$` yields the next value of the iterator.

Iterators are always truthy.


## Function Composition

Functions, types, and type aliases in Samarium can be composed together by using
the `&` operator:

```sm
(<-math.sqrt & <-operator.add)(//, //\)!  == 3
(<-types.Boolean & /?!)("1")!  == true
```
```sm
<=math.[abs, max, min];
arrmap: []?! & <-iter.map;
arrmap(abs, [/, `/, //\, -/\\, -/\/])!  == [1, 0.5, 6, 4, 5]

high x * { * min([x, /\/]); }
low x * { * max([x, \]); }
clamp: high & low;

x: []?!(<<-//../\\/>>)!  == [-3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8]
arrmap(clamp, x)!  == [0, 0, 0, 0, 1, 2, 3, 4, 5, 5, 5, 5]
```
```sm
compose funcs... * {
    * <-iter.reduce(<-operator.and, funcs);
}

repeat_function func times * {
   * compose(**[func]++times);
}

foo x * {
    out: x +++ /?!("0.1")!
    * out;
}

repeat_function(foo, /\/)(`/);
== 0.9330329915368074
== 0.9930924954370359
== 0.9993070929904525
== 0.9999306876841536
== 0.999993068552217
```