# Slices

Slices are used to access a range of items in an iterable (strings, arrays,
tables). They're enclosed in double angle brackets.
Slices have three optional parameters delimited by `..`
— `start`, `stop`, and `step`.

Slices can be either applied to indexable objects (like `String` or `Array`)
or serve as stand-alone objects. Slice objects are hashable.

Iterating over a slice object generates integers from `start` (inclusive)
to `stop` (exclusive) separated by gaps of size `step`.

If `start` is not specified, it defaults to 0.  
If `stop` is not specified, it defaults to 2<sup>63</sup> - 1.  
If `step` is not specified, it defaults to 1. 

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
`<<..stop>>`            | items up to index `stop`
`<<....step>>`          | items separated by gaps of size `step`
`<<start..>>`           | items starting from index `start`
`<<..stop..step>>`      | items up to index `stop` separated by gaps of size `step`
`<<start....step>>`     | items starting from index `start` separated by gaps of size `step`
`<<start..stop>>`       | items starting from index `start` up to index `stop`
`<<start..stop..step>>` | items starting from index `start` up to index `stop` separated by gaps of size `step`
