# Strings

Strings are defined using double quotation marks:

```sm
str: "Hello!";
```

Multiline strings do not require any additional syntax:

```sm
"This
is a
multiline
string"
```


## Basic Operations

Strings can be manipulated using some arithmetic operators:

> `"hello" + "world"` is the same as `"helloworld"`

> `"hello" ++ //` (or `// ++ "hello"`) is the same as `"hellohellohello"`  
> `"hello"++` is the same as `"hello" ++ /\`

> `"hello" - "l"` is the same as `"helo"` (the 2nd operand removes the first
> instance of itself from the 1st operand)

> `"hello" -- "l"` is the same as `"heo"` (the 2nd operand removes all occurences
> of itself from the 1st operand)


## Formatting

Strings can be formatted using the `---` operator.
The 2nd operand can be a String, Array, or a Table.
```sm
"Hi $0!" --- "Bob"!;
== Hi Bob!

"$0$1$0" --- ["abra", "cad"]!;
abracadabra

s: "Coordinates: $lat, $long";
coords: {{
    "lat" -> "56.37N",
    "long" -> "-8.34W"
}};
s --- coords!;
== Coordinates: 56.37N, -8.34W
```


## Casting

Strings can be casted to Integers (for single characters) or Arrays of Integers
(for longer strings), representing the Unicode code point of each character:

> `"a"%` returns `97`.

> `"hi!"%` returns `[104, 105, 33]`.


## Shifting

Strings can have their characters shifted by adding/subtracting numbers.
For example, `"hi" + /` will result in the string `"ij"`, where each character
in the string has been shifted one position ahead. Similarly, `"hi" - /` will
result in the string `"gh"`, where each character in the string has been shifted
one position backwards.
