# `iter` module

The `iter` module contains several functions that interact with iterable
objects, like strings or arrays.

<center>

Function                        | Use
---                             | ---
`accumulate(array, function)`   | Yields accumulated applications of `function`[^2]<br>on consecutive elements of `array`.<br>If for example `function` returned the sum of both of its arguments,<br>then `accumulate([/, /\, //, /\\, /\/], function)`<br>would yield `1`, `3`, `6`, `10`, and `15`.
`all(array)`                    | Returns `1` if all elements of `array` are truthy,<br>`0` otherwise. Returns `1` for empty arrays.
`any(array)`                    | Returns `1` if any of the elements of `array` is truthy,<br>`0` otherwise. Returns `0` for empty arrays.
`chunks(array, size)`           | Iterates over `array` in chunks of size `size`.<br>When `array`'s length is not evenly divided by `size`,<br>the last slice of `array` will be the remainder.
`cycle(iter)`                   | Copies an iterable by consuming it,<br>and yields its elements in an infinite cycle.
`count(array, target)`          | Returns the number of times `target` appears in `array`.
`drop_while(array, function)`   | Evaluates `function`[^1] on each item of `array`,<br>and yields elements of `array` starting from the first item<br>(from the left) for which `function` returns a falsy value.
`filter(function, array)`       | Evaluates `function`[^1] on each item of `array`,<br>and yields those items that cause `function` to return a truthy value.
`filter_false(function, array)` | Evaluates `function`[^1] on each item of `array`,<br>and yields those items that cause `function` to return a falsy value.
`find(array, target)`           | Finds the first instance of `target` in `array`, and returns its index.<br>`array` may be of type Array or String.<br>If `target` does not appear in `array`, `-1` is returned instead.
`find_all(array, target)`       | Finds all instances of `target` in `array`, and yields their indices.
`flatten(array[, depth])`       | Flattens `array` `depth` times.<br>By default, flattens recursively as deep as possible.
`map(function, array)`          | Applies `function`[^1] to each item of `array`, and yields those new values.
`pairwise(array)`               | Yields successive overlapping pairs taken from `array`.
`reduce(function, array)`       | Applies `function`[^2] cumulatively to consecutive items of `array`,<br>reducing it to a single value, then returns this value.<br>Equivalent to `[i ... i ->? accumulate(array, function)]<<-/>>`.
`reverse(array)`                | Yields the items of `array` in reverse order.
`sorted(array[, key])`          | Returns a sorted copy of `array`.<br>The optional parameter `key` specifies a function[^1] that is used<br>to extract a comparison key from each element in `array`.<br>Elements are compared directly by default. 
`take_while(array, function)`   | Evaluates `function`[^1] on each item of `array`,<br>and yields elements of `array` that is cut off at the first item<br>(from the left) for which `function` returns a falsy value.
`zip_longest(fill, arrays...)`  | Iterates over several arrays, producing a set of arrays<br>containing an item from each original array.<br>If the arrays are of uneven length,<br>missing values are filled using the `fill` argument.

</center>

[^1]: Note that `function` must take only one argument (excluding optional
parameters).

[^2]: Note that `function` must take exactly two arguments (excluding optional
parameters).
