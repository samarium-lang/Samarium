# `iter` module

The `iter` module contains several functions that interact with iterable objects, like strings or arrays.

Function                        | Use
---                             | ---
`accumulate(array, function)`   | Yields accumulated applications of `function` on consecutive elements of `array`.<br>If for example `function` returned the sum of both of its arguments, then `accumulate([/, /\, //, /\\, /\/], function)` would yield `1`, `3`, `6`, `10`, and `15`.[^2]
`all(array)`                    | Returns `1` if all elements of `array` are truthy, `0` otherwise. Returns `1` for empty arrays.
`any(array)`                    | Returns `1` if any of the elements of `array` is truthy, `0` otherwise. Returns `0` for empty arrays.
`count(array, target)`          | Returns the number of times `target` appears in `array`.
`drop_while(array, function)`   | Evaluates `function` on each item of `array`, and yields elements of `array` starting from the first item (from the left) for which `function` returns a falsy value.[^1]
`enumerate(array)`              | Yields elements of `array` but with each item as a length 2 array containing the item's index paired with the original item.
`filter(array, function)`       | Evaluates `function` on each item of `array`,<br>and yields those items that cause `function` to return a truthy value.[^1]
`filter_false(array, function)` | Evaluates `function` on each item of `array`,<br>and yields those items that cause `function` to return a falsy value.[^1]
`find(array, target)`           | Finds the first instance of `target` in `array`, and returns its index.<br>`array` may be of type Array or String. If `target` does not appear in `array`, `-1` is instead returned.
`find_all(array, target)`       | Finds all instances of `target` in `array`, and yields their indices.
`map(array, function)`          | Applies `function` to each item of `array`, and yields those new values.[^1]
`pairwise(array)`               | Yields successive overlapping pairs taken from `array`.
`reduce(array, function)`       | Applies `function` cumulatively to consecutive items of `array`, reducing it to a single value, then returns this value.<br>Equivalent to `[i ... i ->? accumulate(array, function)]<<-/>>`.[^2]
`reverse(array)`                | Yields the items of `array` in reverse order.
`sort(array)`                   | Returns a sorted copy of `array`, using the comparison operators `<`, `>`, etc.
`take_while(array, function)`   | Evaluates `function` on each item of `array`, and yields elements of `array` that is cut off at the first item (from the left) for which `function` returns a falsy value.[^1]
`zip(arrays)`                   | Iterates over several iterables in parallel, producing arrays with an item from each one.
`zip_longest(fill, arrays...)`  | Iterates over several arrays, producing a set of arrays containing an item from each original array.<br>If the arrays are of uneven length, missing values are filled using the `fill` argument.


[^1]: Note that `function` must take only one argument (excluding optional parameters).

[^2]: Note that `function` must take exactly two arguments (excluding optional parameters).
