# Slices

Slices are used to access a range of items in an iterable (strings, arrays, tables).
They don't do anything by themselves.
Slices are enclosed in double angle brackets.
They have three parameters, `start`, `stop` and `step`, any of which may be omitted.
`..` is used to indicate `stop`, and `**` is used to indicate `step`.

<p align="left">
    <img src="images/14slice.png" style="transform: scale(0.6)">
</p>

All valid slice parameters are as follows:
Slice                   | Returns
---                     | ---
`<<>>`                  | the whole iterable
`<<index>>`             | the item at position `index`
`<<..stop>>`            | all items up to index `stop`
`<<**step>>`            | all items separated by gaps of size `step`
`<<start..>>`           | all items starting from index `start`
`<<..stop**step>>`      | all items up to index `stop` separated by gaps of size `step`
`<<start**step>>`       | all items starting from index `start` separated by gaps of size `step`
`<<start..stop>>`       | all items starting from index `start` up to index `stop`
`<<start..stop**step>>` | all items starting from index `start` up to index `stop` separated by gaps of size `step`
