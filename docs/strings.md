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

Strings can be manipulated using some arithmetic operators:

`"hello" + "world"` is the same as `"helloworld"`

`"hello" ++ //` is the same as `"hellohellohello"`

Strings can be casted to Integers (for single characters) or Arrays of Integers
(for longer strings), representing the Unicode code point of each character:

`"a"%` returns `97`.

`"hi!"%` returns `[104, 105, 33]`.