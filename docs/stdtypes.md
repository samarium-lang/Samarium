# `types` module

The `types` module implements native data type aliases and data types not
built-in to the language itself.


## Additional types


### Boolean

The Boolean type can have value either `true` or `false`.

Booleans can be initialized with either a string with the value `"true"` or
`"false"`, or a truthy/falsy value. Booleans support several operations: all
comparison operations, all arithmetic operations, all bitwise operations, and
can be used with logical operators, and converted to a string (specifically
either `"true"` or `"false"`).


### Frozen

`Frozen` is a wrapper type designed to allow mutable types like Arrays and
Tables to be used as keys in a Table. `Frozen` is immutable, meaning that once a
value has been wrapped in a Frozen, it cannot be changed.

```sm
test_key key * {
    ?? { {{key -> <-math.sum(key)}}!; }
    !! { "invalid key:", key!; }
}

test_key([//, /\\]);  == invalid key: [3, 4]
test_key(<-types.Frozen([//, /\\]));  == {{Frozen([3, 4]) -> 7}}
```



### UUID4

Generates a random UUID, version 4.
Returns a UUID object with attributes `hex` and `dec`:

```sm
<=types.UUID4;

uuid: UUID4();
uuid!;
== 8b46f521-b821-4010-ae8f-9ae9522d9889

uuid.hex!;
== "8b46f521b8214010ae8f9ae9522d9889"

uuid.dec!;
== 185131124056068440795959350641466120329
```


## Built-in type aliases


### Array

The `Array` type alias is defined to be equal to `[]?!`.

Calling `Array()` with no arguments will return an empty array.

A copy of an array `a` can be made by using `Array(a)`.

```sm
a: [/, /\, //];
b: a;
c: Array(a);
d: a<<>>;

a<</\>>: /\\;
a, b, c, d!;
```

Arrays can also be constructed from strings and tables:  

> `Array("ball")` is equivalent to `["b", "a", "l", "l"]`  
> `Array({{// -> /\\, "X" -> "D" }})` is equivalent to `[[//, /\\], ["X", "D"]]`


### Number

The `Number` type alias is defined to be equal to `\?!`.

Caling `Number()` with no arguments will return the number `0`.

Numbers can be constructed from strings, including
binary, octal, and hexadecimal representations:  

> `Number("1000")` will return `1000`  
> `Number("b:1000")` will return `8`  
> `Number("o:1000")` will return `512`  
> `Number("x:1000")` will return `4096`

Floats can also be supplied:
> `Number("3.14")` will return `3.14`  
> `Number("x:3.23d70a3d70a3e")` will return `3.14`  
> `Number("o:23.6560507534121727")` will return `19.84`

Scientific notation is also supported, with `significand[e]exponent` for bases
2, 8 and 10, and `significand[p]exponent` for base 16:
> `Number("b:0.11e11")` will return `6`  
> `Number("o:5e7")` will return `10485760`  
> `Number("1e-3")` will return `0.001`  
> `Number("x:0.2p7")` will return `16`


### Null

The `Null` type alias is defined to be equal to `(||)?!`. It can be used for
explicit null values instead of relying on implicit null triggers.


### Slice

The `Slice` type alias is defined to be equal to `<<>>?!`.

Different slices can be constructed by using integers and nulls:  

- `Slice(/, /\, //)` is equivalent to `<</../\..//>>`
- `Slice(, , -/)` is equivalent to `<<....-/>>`
- `Slice(/, , ,)` is equivalent to `<</..>>`
- `Slice(, /\/, ,)` is equivalent to `<<../\/>>`


### String

The `String` type alias is defined to be equal to `""?!`.

Calling `String()` with no arguments will return an empty string.

Any data type can be converted to a string.

A copy of a string `s` can be made by using `String(s)`.


### Table

The `Table` type alias is defined to be equal to `{{}}?!`.

Calling `Table()` with no arguments will return an empty table.

Tables can be constructed from arrays containing 2-element iterables:<br>
`Table([[//, /\\/], "XD"])` is equivalent to `{{// -> /\\/, "X" -> "D"}}`

### Zip

The `Zip` type alias is defined to be equal to `("" >< "")?!`.

Calling `Zip()` with no arguments will return an empty iterator.
Passing in only 1 argument is equivalent to `... i ->? iter { ** [i]; }`.
Calling `Zip()` with 2 or more arguments is equivalent to using the `><`
operator on them.