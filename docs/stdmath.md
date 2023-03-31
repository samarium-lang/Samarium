# `math` module

The `math` module provides access to a set of commonly used mathematical
functions and constants.

Constants:

- `math.E` (e: 2.718281828459045...)
- `math.PHI` (φ: 1.618033988749894...)
- `math.PI` (π: 3.141592653589793...)

<center>

Function                             | Use
---                                  | ---
`abs(n)`                             | Returns the absolute value of `n`.
`ceil(x)`                            | Returns the least integer ≥ `x`.
`factorial(n)`                       | Returns `n` factorial.
`floor(x)`                           | Returns the greatest integer ≤ `x`.
`gcd(a, b)`                          | Returns the greatest common divisor of `a` and `b`.<br>If either argument is zero, the absolute value of the other argument will be returned.
`is_int(x)`                          | Returns `1` if `x` is an integer, `0` otherwise. Equivalent to `x :: x$`.
`is_prime(n)`                        | Returns `1` if `n` is prime, `0` otherwise.
`lcm(a, b)`                          | Returns the least common multiple of `a` and `b`.<br>If any of the arguments is zero,<br> then the returned value is `0`.
`max(array)`                         | Returns the largest integer in `array`.
`min(array)`                         | Returns the smallest integer in `array`.
`product(array)`                     | Multiplies the items of `array` from left to right and returns the total.<br>The `array`'s items must be integers.
`round(x[, ndigits])`                | Returns `x` rounded to `ndigits` precision after the decimal point.<br>Works exactly like Python's [`round()`](https://docs.python.org/3/library/functions.html#round).
`shl(a, b)`                          | Returns `a` shifted to the left by `b` bits.
`shr(a, b)`                          | Returns `a` shifted to the right by `b` bits.
`sqrt(x)`                            | Returns the integer square root of the nonnegative integer `n`.<br>This is the floor of the exact square root of `n`.
`sum(array[, start])`                | Sums `start` and the items of `array` from left to right and returns the total.<br>`start` defaults to `0`.
`to_bin(n)`                          | Returns the binary representation of `n` as a string.
`to_oct(n)`                          | Returns the octal representation of `n` as a string.
`to_hex(n)`                          | Returns the hexadecimal representation of `n` as a string.

</center>
