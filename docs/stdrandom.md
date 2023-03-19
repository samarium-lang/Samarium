# `random` module

The `random` module implements functions that make use of the
[random method `??`](builtins.md#RANDOM).

Function           | Use
---                | ---
`choices(iter, k)` | Randomly selects an item from `iter` `k` times<br>and returns the resulting choices as an array.
`randint(a, b)`    | Returns a random integer in range [a, b].
`sample(array, k)` | Randomly selects `k` unique items from `array`,<br>and returns the resulting choices as an array.
`shuffle(array)`   | Randomly shuffles `array` and returns the result. `array` must be of type Array.
