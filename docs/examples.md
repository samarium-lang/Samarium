# Examples


## Reverse a file's contents

```sm
=> argv * {
    file: argv<</>>;
    data <~ file;
    data<<....-/>> ~> file;
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
    out: [];
    ... i, v ->? <<>> >< array {
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
    !! n >: \;
    ? ~~ n {
        * /;
    }
    * n ++ factorial(n - /);
}
```


## Variable Arguments

```sm
point coords... * {
    * "(" + <-string.join(coords, ", ") + ") is a " + ""?!(coords$) + "D point";
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
    nums: <</../\//>>!;
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
random_hex_color * {
    * "#" + <-string.join([<-string.hexdigits?? ... i ->? <<../\\>>]);
}

== could alternatively define that as

random_hex_color * {
    max: /\ +++ //\\\;
    * "#" + <-string.leftpad(<-math.to_hex(max??), //\, "0");
}

=> * {
    random_hex_color()!;     == #d2300a
    random_hex_color()!;     == #f866ce
    random_hex_color()!;     == #8fb3cf
}
```


## Optional Arguments

```sm
roll_dice q? * {
    roll1 * { * //\?? + /; }
    q <> /;
    ? q :: / {
        * roll1();
    } ,, {
        * [roll1() ... i ->? <<..q>>];
    }
}

=> * {
    roll_dice()!;       == 5
    roll_dice(/\)!;     == [6, 3]
    roll_dice(/\\/\/)!;
    == [5, 5, 6, 4, 6, 5, 6, 4, 5, 4, 4, 6, 5, 3, 6, 6, 2, 1, 4, 5, 5, 1, 2, 1]
}
```


## Classes

```sm
@ Rectangle {
    create a b * {
        'a: a;
        'b: b;
    }

    to_string * {
        * "Rectangle[" + ""?!('a) + ", " + ""?!('b) + "]";
    }

    circumference * {
        * 'a ++ /\ + 'b ++ /\;
    }

    area * {
        * 'a ++ 'b;
    }

    is_square * {
        * 'a :: 'b;
    }
}

=> * {
    r: Rectangle(/\\, //);
    r!;                  == Rectangle[4, 3]
    r.circumference()!;  == 14
    r.area()!;           == 12
    r.is_square()!;       == 0
}
```

## Decorators

```sm
log_call func * {
    wrapper args... * {
        "Calling function", func, "with args", args!;
        * func(**args);
    }
    * wrapper;
}

log_call @ pow a b * {
    * a +++ b;
}

=> * {
    pow(/\, //)!;
    == Calling function pow with args [2, 3]
    == 8
}
```
