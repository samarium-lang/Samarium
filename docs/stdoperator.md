# `operator` module

This module contains a set of functions corresponding to the native operators of Samarium. For instance, `operator.mul(a, b)` is equivalent to `a ++ b`. Each of the function names can be used for defining special methods in classes.

Function                      | Operator
---                           | ---
`add(x, y)`                   | `x + y`
`and(x, y)`                   | `x & y`
`cast(x)`                     | `x%`
`divide(x, y)`                | `x -- y`
`equals(x, y)`                | `x :: y`
`greater_than(x, y)`          | `x > y`
`greater_than_or_equal(x, y)` | `x >: y`
`has(x, y)`                   | `y ->? x`
`hash(x)`                     | `x##`
`less_than(x, y)`             | `x < y`
`less_than_or_equal(x, y)`    | `x <: y`
`mod(x, y)`                   | `x --- y`
`multiply(x, y)`              | `x ++ y`
`not(x)`                      | `~x`
`not_equals(x, y)`            | `x ::: y`
`or(x, y)`                    | `x | y`
`power(x, y)`                 | `x +++ y`
`random(x)`                   | `x??`
`special(x)`                  | `x$`
`subtract(x, y)`              | `x - y`
`to_bit(x)`                   | `x.to_bit()`
`to_string(x)`                | `x.to_string()`
`xor(x, y)`                   | `x ^ y`
