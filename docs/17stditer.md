# `iter` module

The `iter` module contains several functions that interact with iterable objects, like strings or arrays.

Function                       | Use
---                            | ---
`find(array, target)`          | Finds the first instance of `target` in `array`, and returns its index. `array` may be of type Array or String. If `target` does not appear in `array`, `-1` is instead returned.
`count(array, target)`         | Returns the number of times `target` appears in `array`.
`filter(array, function)`      | Evaluates `function` on each item of `array`, and returns a new array with only those items which cause `function` to return a truthy value.[<sup>a</sup>](#note-a)
`filterFalse(array, function)` | Evaluates `function` on each item of `array`, and returns a new array with only those items which cause `function` to return a falsy value.[<sup>a</sup>](#note-a)
`map(array, function)`         | Applies `function` to each item of `array`, and returns a new array with these values.[<sup>a</sup>](#note-a)
`reverse(array)`               | Returns a copy of `array` with the order of its items reversed.
`takeWhile(array, function)`   | Evaluates `function` on each item of `array`, and returns a copy of `array` that is cut off at the first item (from the left) for which `function` returns a falsy value.[<sup>a</sup>](#note-a)
`dropWhile(array, function)`   | Evaluates `function` on each item of `array`, and returns a copy of `array` starting from the first item (from the left) for which `function` returns a falsy value.[<sup>a</sup>](#note-a)
`accumulate(array, function)`  | Returns an array of accumulated applications of `function` on consecutive elements of `array`. If for example `function` returned the sum of both of its arguments, then `accumulate([/, /\, //, /\\, /\/], function)` would return `[1, 3, 6, 10, 15]`.[<sup>b</sup>](#note-b)
`reduce(array, function)`      | Applies `function` cumulatively to consecutive items of `array`, reducing it to a single value, then returns this value. Equivalent to `accumulate(array, function)<<-/>>`.[<sup>b</sup>](#note-b)
`enumerate(array)`             | Returns a copy of `array` but with each item as a length 2 array containing the item's index paired with the original item.
`range(start, stop[, step])`   | Generates an array of integers from `start` (inclusive) to `stop` (exclusive) separated by gaps of size `step`. If only one argument is provided, it will apply to `stop`, and `start` will default to `0`. If a value for `step` is not provided, it will default to `1`. Commonly used in [`foreach` loops](09controlflow.md#foreach-loop).
`sort(array)`                  | Returns a sorted copy of `array`, using the comparison operators `<`, `>`, etc.
`all(array)`                   | Returns `1` if all elements of `array` are truthy, `0` otherwise. Returns `1` for empty arrays.
`any(array)`                   | Returns `1` if any of the elements of `array` is truthy, `0` otherwise. Returns `0` for empty arrays.
`findAll(array, target)`       | Finds all instances of `target` in `array`, and returns an array of their indices.
`pairwise(array)`              | Returns successive overlapping pairs taken from `array`.
`zip(arrays)`                  | 
`zipLongest(arrays, fill)`     | 

<sup id="note-a">a</sup> Note that `function` must take only one argument (excluding default arguments).

<sup id="note-b">b</sup> Note that `function` must take exactly two arguments (excluding default arguments).