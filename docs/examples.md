# Examples

## Reverse a file's contents

```sm
=> argv * {
    file: argv<</>>;
    data <~ file;
    data<<**-/>> ~> file;
}
```

## Truth Machine

```sm
=> * {
    ? ??? :: "1" {
        .. { "1"!; }
    }
    "0"!;
    =>!;
}
```

## Dropsort

```sm
dropsort array * {
    <-iter.enumerate;
    out: [];
    ... i, v ->? enumerate(array) {
        ? ~~ out || v >: out<<-/>> {
            out+: [v];
        }
    }
    * out;
}
```

## Factorial

```sm
factorial n * {
    # n >: \;
    ? ~~ n {
        * /;
    }
    * n ++ factorial(n - /);
}
```


## Variable Arguments

```sm
point coords... * {
    <-string.join;
    <-types.String;
    * "(" + join(coords, ", ") + ") is a " + String(coords$) + "D point";
}

=> * {
    point()!;                     == () is a 0D point
    point(\)!;                    == (0) is a 1D point
    point(//, -/\\)!;             == (3, -4) is a 2D point
    point(-/\, /\\, -/\/)!;       == (-2, 4, -5) is a 3D point
    point(///, -///, -/\/, -/)!;  == (7, -7, -5, -1) is a 4D point
}
```

## Loop Flow

```sm
=> * {
    <-iter.range;
    nums: range(/, /\//)!;
    ... n ->? nums {
        ? n --- /\ :: \ { -> }
        ? n :: /\\/ { <- }
        n!;
    }
}

==<
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
1
3
5
7
>==
```

## Randomness

```sm
randomHexColor * {
    <-iter.range;
    <-string.hexdigits, join;
    * "#" + join([hexdigits?? ... i ->? range(/\\)]);
}

== could alternatively define that as

randomHexColor * {
    max: /\ +++ //\\\;
    <-string.leftpad;
    <-math.toHex;
    * "#" + leftpad(toHex(max??), //\, "0");
}

=> * {
    randomHexColor()!;     == #d2300a
    randomHexColor()!;     == #f866ce
    randomHexColor()!;     == #8fb3cf
}
```

## Optional Arguments

```sm
rollDice q? * {
    roll1 * { * //\?? + /; }
    q <> /;
    ? q :: / {
        * roll1();
    } ,, {
        <-iter.range;
        * [roll1() ... i ->? range(q)];
    }
}

=> * {
    rollDice()!;       == 5
    rollDice(/\)!;     == [6, 3]
    rollDice(/\\/\/)!; == [5, 5, 6, 4, 6, 5, 6, 4, 5, 4, 4, 6, 5, 3, 6, 6, 2, 1, 4, 5, 5, 1, 2, 1]
}
```

## Classes

```sm
@ Rectangle {
    create a b * {
        'a: a;
        'b: b;
    }

    toString * {
        <-types.String;
        * "Rectangle[" + String('a) + ", " + String('b) + "]";
    }

    circumference * {
        * 'a ++ /\ + 'b ++ /\;
    }

    area * {
        * 'a ++ 'b;
    }

    isSquare * {
        * 'a :: 'b;
    }
}

=> * {
    r: Rectangle(/\\, //);
    r!;                  == Rectangle[4, 3]
    r.circumference()!;  == 14
    r.area()!;           == 12
    r.isSquare()!;       == 0
}
```

## Decorators

```sm
logCall func * {
    wrapper args... * {
        "Calling function", func, "with args", args!;
        * func(**args);
    }
    * wrapper;
}

logCall @ pow a b * {
    * a +++ b;
}

=> * {
    pow(/\, //)!;
    == Calling function pow with args [2, 3]
    == 8
}
```
