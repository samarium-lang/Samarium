# Examples


## Reverse a file's contents

```sm
=> argv * {
    file: argv<</>>;
    data <~ file;
    data<<....-/>> ~> file;
}
```


## Counting duplicates

```sm
arr: <-io.inputcast("Enter an array of values: ");
"Found $0 duplicate(s) in the array" --- [arr$ - (-arr)$]!;
```


## Checking Pythagorean triplets

```sm
a, b, c: <-iter.sorted(<-io.inputcast("Enter three integers: "));
"These numbers do $0form a Pythagorean triplet"
--- ["not " ++ (~~(a+++ + b+++ :: c+++))]!;
```


## Generating a password

```sm
CHARSET: <-string.LETTERS + <-string.DIGITS;
... c ->? [CHARSET?? ... _ ->? <<../?!("Password length: "???)>>] { c ~> /; }!;
```


## Factorial function

```sm
factorial n * {
    !! n>:, "n cannot be negative";
    ? ~~ n { * /; }
    * n ++ factorial(n-);
}

n: /?!("n: "???);
"n! =", factorial(n)!;
```


## Memoization

```sm
<=types.Frozen;

memoize func * {
    cache: {{}};
    wrapper args... * {
        args: Frozen(args);
        ? args ->? cache { * cache<<args>>; }
        result: func(**args);
        cache<<args>>: result;
        * result;
    }
    * wrapper;
}

memoize @ fib n * {
    ? n < /\ { * n; }
    * fib(n-) + fib(n - /\);
}

fib(///\/)!;
```


## Filtering and enumerating a file

```sm
== Reads URLs from a file, enumerates them and prints them out.
== If a URL is 32 characters or longer, it will be printed in red.
<=string.[to_upper, strip];

urls <~~ "urls.txt";
... lineno, line ->? <</..>> >< urls {
    line: strip(line);
    ? line$ > ///// {
        line: "\033[31m$0\033[0m" --- line;
    }
    "$0. $1" --- [lineno, line]!;
}
~urls;
```


## Guess the number game

```sm
"Guess the number!"!;
secret_number: (/\/\+++)??+;

.. {
    guess: "Please input your guess: "???;

    ?? { guess: /?!(guess); }
    !! { -> }

    "You guessed:", gues!;

    ? guess < secret_number { "Too small!"!; -> }
    ? guess > secret_number { "Too big!"!; -> }

    "You win!"!;
    <-
}
```


## Point class implementation

```sm
<=operator -> op;
<=iter.map;

@ Point {
    => scalars... * { 'vector: scalars; }
    ! * { * "($0)" --- <-string.join('vector, ", "); }
    ... * { ... i -.? 'vector { **i; } }
    magnitude * { * <-math.sum('vector) +++ `/; }

    -   other * { * Point(**map(op.sub, ' >< other)); }
    +   other * { * Point(**map(op.add, ' >< other)); }
    --  other * { * Point(**map(op.div, ' >< other)); }
    ++  other * { * Point(**map(op.mul, ' >< other)); }
    --- other * { * Point(**map(op.mod, ' >< other)); }
    ><  other * { * 'vector >< other.vector; }
    +++ other * {
        out: [];
        ... a ->? 'vector {
            ... b ->? other.vector { out+: [[a, b]]; }
        }
        * -out;
    }
}

q, p: Point(/\, //, /\\), Point(//, /\\, /\/);

p.magnitude()!;  == 3.4641016151377544
[]?!(q)!;  == [2, 3, 4]

p + q!;    == (5, 7, 9)
p - q!;    == (1, 1, 1)
p ++ q!;   == (6, 12, 20)
p --- q!;  == (1, 1, 1)
p +++ q!;
== [
==     [3, 2], [3, 3], [3, 4],
==     [4, 2], [4, 3], [4, 4],
==     [5, 2], [5, 3], [5, 4]
== ]
```


## Optional arguments

```sm
rect_area length width? * {
    width <> length;
    * width ++ length;
}

rect_area(/\/, /\\\)!;  == 40
rect_area(/\/)!;  == 25
```
