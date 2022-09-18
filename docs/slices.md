# Slices

Slices are used to access a range of items in an iterable (strings, arrays, tables).
They don't do anything by themselves.
Slices are enclosed in double angle brackets.
They have three optional parameters, `start`, `stop`, and `step`, delimited by `..`.

```sm
str: "abcdefgh";
str<<\>> :: "a";
str<<//..//\>> :: "def";
str<</..//\../\>> :: "bdf";
```

All valid slice parameters are as follows:
Slice                   | Returns
---                     | ---
`<<>>`                  | the whole iterable
`<<index>>`             | the item at position `index`
`<<..stop>>`            | all items up to index `stop`
`<<....step>>`          | all items separated by gaps of size `step`
`<<start..>>`           | all items starting from index `start`
`<<..stop..step>>`      | all items up to index `stop` separated by gaps of size `step`
`<<start....step>>`     | all items starting from index `start` separated by gaps of size `step`
`<<start..stop>>`       | all items starting from index `start` up to index `stop`
`<<start..stop..step>>` | all items starting from index `start` up to index `stop` separated by gaps of size `step`
