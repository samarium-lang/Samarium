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


Arrays of Integers can be cast to type String:

> `[//\/\\\, //\/\\/, ////\\/, //\\\\/]%` gives `"hiya"`