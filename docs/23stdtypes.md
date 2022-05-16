[Back](18stdstring.md) | [Table of Contents](tableofcontents.md)
---                    | ---

# `types` module

The `types` module implements native data type aliases and data types not built-in to the language itself.

## Additional types

### Boolean

The Boolean type can have value either `true` or `false`.

Booleans can be initialized with either a string with the value `"true"` or `"false"`, or a truthy/falsy value.
Booleans support several operations: all comparison operations, all arithmetic operations, all bitwise operations, and can be used with logical operators, and converted to a string (specifically either `"true"` or `"false"`).

### UUID4

Generates a random UUID, version 4. Returns a UUID object with attributes `hex` and `dec`:
```
<-types.UUID4;

uuid: UUID4();
uuid!;
== 8b46f521-b821-4010-ae8f-9ae9522d9889

uuid.hex!;
== 8b46f521b8214010ae8f9ae9522d9889

uuid.dec!;
== 185131124056068440795959350641466120329
```

## Built-in type aliases

### Array

The `Array` type alias is defined to be equal to `[]?!`.

Caling `Array()` with no arguments will return an empty array.

A copy of an array `a` can be made by using `Array(a)`.
```
a: [/, /\, //];
b: a;
c: Array(a);
d: a<<>>;

a<</\>> = /\\;
a, b, c, d!;
```

Arrays can also be constructed from strings and tables:
- `Array("ball")` is equivalent to `["b", "a", "l", "l"]`
- `Array({{// -> /\\/, "X" -> "D" }})` is equivalent to `[[//, /\\/], ["X", "D"]]`

### Integer

The `Integer` type alias is defined to be equal to `\?!`.

Caling `Integer()` with no arguments will return the integer `0`.

Integers can be constructed from strings, including binary, octal, and hexadecimal representations:
- `Integer("1000")` will return `1000`
- `Integer("b:1000")` will return `8`
- `Integer("o:1000")` will return `512`
- `Integer("x:1000")` will return `4096`

### Null

The `Null` type alias is defined to be equal to `_?!`. Using this type alias is no different than using the literal `_`.

### Slice

The `Slice` type alias is defined to be equal to `<<>>?!`.

Different slices can be constructed by using integers and nulls:
- `Slice(/, /\, //)` is equivalent to `<</../\**//>>`
- `Slice(_, _, -/)` is equivalent to `<<**-/>>`
- `Slice(/, _, _)` is equivalent to `<</..>>`
- `Slice(_, /\/, _)` is equivalent to `<<../\/>>`

### String

The `String` type alias is defined to be equal to `""?!`.

Calling `String()` with no arguments will return an empty string.

Any data type can be converted to a string.

A copy of a string `s` can be made by using `String(s)`.

### Table

The `Table` type alias is defined to be equal to `{{}}?!`.

Calling `Table()` with no arguments will return an empty table.

Tables can be constructed from arrays containing 2-element iterables:
- `Table([[//, /\\/], "XD"])` is equivalent to `{{// -> /\\/, "X" -> "D"}}`