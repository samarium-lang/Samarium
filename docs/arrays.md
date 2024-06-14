# Arrays

Arrays are defined using square brackets, with items separated by commas:

```sm
[\, /\, //]
```

Arrays can be concatenated with the `+` operator:

> `[/, /\] + [//]` is the same as `[/, /\, //]`

To remove items from an array, the `-` operator can be used with either an index
or a value. When removing by value, only the first instance of each value will
be removed. Trying to remove an element not present in the array will result in
an error.

> `["a", "b", "c"] - /` gives `["a", "c"]`  
> `["a", "b", "c", "d"] - ["b", "d"]` gives `["a", "c"]`

`--` can be used instead if we want to remove elements even if they're not
present in the array:

> `["a", "b", "c", "d"] - ["c", "d", "e"]` gives `["a", "b"]`

Negating an array will return its copy with duplicates removed:

> `-[/\\\, //, //, //\, /\\\, //, /\/]` gives `[/\\\, //, //\, /\/]`

If we want to remove duplicates of just one value, we can use `---`:

> `[/\\\, //, //, //\, /\\\, //, /\/] --- //` gives `[/\\\, //, //\, /\\\, /\/]`

Set-like union, intersection, and symmetric difference can be obtained by using
`|`, `&` and `^`, respectively:

```sm
primes: [/\, //, /\/, ///, /\//, //\/]!;
evens: [/\, /\\, //\, /\\\, /\/\, //\\]!;

"|", primes | evens!;
"&", primes & evens!;
"^", primes ^ evens!;
```
```
[2, 3, 5, 7, 11, 13]
[2, 4, 6, 8, 10, 12]
| [2, 3, 5, 7, 11, 13, 4, 6, 8, 10, 12]
& [2]
^ [3, 5, 7, 11, 13, 4, 6, 8, 10, 12]
```

Arrays of integers can be cast to type String:

> `[//\/\\\, //\/\\/, ////\\/, //\\\\/]%` gives `"hiya"`