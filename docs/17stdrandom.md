# `random` module

The `random` module implements functions that make use of the [random number generator `^^`](01integers.md#random-numbers).

Function           | Use
---                | ---
`choice(iter)`     | Returns a random item from `iter`. `iter` may be of type Array or String. `iter` must not be empty.
`shuffle(array)`   | Randomly shuffles `array` and returns the result. `array` must be of type Array.
`choices(iter, k)` | Randomly selects an item from `iter` `k` times and returns the resulting choices as an array.
`sample(array, k)` | Randomly selects `k` unique items from `array`, and returns the resulting choices as an array.
