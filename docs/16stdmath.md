[Back](15stditer.md) | [Table of Contents](../README.md#table-of-contents) | [Next](17stdrandom.md)
---                  | ---                                                 | ---

# `math` module

The `math` module provides access to a set of commonly used mathematical functions.

Function              | Use
---                   | ---
`abs(n)`              | Returns the absolute value of `n`.
`factorial(n)`        | Returns `n` factorial.
`gcd(a, b)`           | Returns the greatest common divisor of `a` and `b`. If either argument is zero, the absolute value of the other argument will be returned.
`lcm(a, b)`           | Returns the least common multiple of `a` and `b`. If any of the arguments is zero, then the returned value is `0`.
`product(array)`      | Multiplies the items of `array` from left to right and returns the total. The `array`'s items must be integers.
`sum(array)`          | Sums the items of `array` from left to right and returns the total. The `array`'s items must be integers.
`max(array)`          | Returns the largest integer in `array`.
`min(array)`          | Returns the smallest integer in `array`.
`fromDecimal(string)` | Returns an `Integer` object constructed from `string`, or returns `0` if `string` is an empty string. Obsolete with the addition of [using types as functions](08builtins.md#typeof).
`sqrt(n)`             | Returns the integer square root of the nonnegative integer `n`. This is the floor of the exact square root of `n`.
`shl(a, b)`           | Returns `a` shifted to the left by `b` bits.
`shr(a, b)`           | Returns `a` shifted to the right by `b` bits.
