[Back](16stdmath.md) | [Table of Contents](tableofcontents.md) | [Next](18stdstring.md)
---                  | ---                                     | ---

# `random` module

The `random` module implements functions that make use of the [random number generator `^^`](01integers.md#random-numbers).

Function           | Use
---                | ---
`randint(a, b)`    | Returns a random integer in range [a, b].
`shuffle(array)`   | Randomly shuffles `array` and returns the result. `array` must be of type Array.
`choices(iter, k)` | Randomly selects an item from `iter` `k` times and returns the resulting choices as an array.
`sample(array, k)` | Randomly selects `k` unique items from `array`, and returns the resulting choices as an array.
