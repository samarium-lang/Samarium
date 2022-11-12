# Arrays

Arrays are defined using square brackets, with items separated by commas:

```sm
[\, /\, //]
```

Arrays can be concatenated with the `+` operator:

`[/, /\] + [//]` is the same as `[/, /\, //]`

Items can also be removed from an array using the `-` operator, either by index or by value. Removing an element by value will remove only the first instance of that value in the array.

`["a", "b", "c"] - /` gives `["a", "c"]`

`["a", "b", "c", "d"] - ["b", "d"]` gives `["a", "c"]`

Arrays of Integers can be casted to Strings:

`[//\/\\\, //\/\\/, ////\\/, //\\\\/]%` gives `"hiya"`