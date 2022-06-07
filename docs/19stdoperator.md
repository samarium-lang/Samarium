# `operator` module

This module contains a set of functions corresponding to the native operators of Samarium. For instance, `operator.mul(a, b)` is equivalent to `a ++ b`. Each of the function names can be used for defining special methods in classes.

Function                   | Operator
---                        | ---
`add(x, y)`                | `x + y`
`and(x, y)`                | `x & y`
`cast(x)`                  | `x%`
`divide(x, y)`             | `x -- y`
`equals(x, y)`             | `x :: y`
`greaterThanOrEqual(x, y)` | `x >: y`
`greaterThan(x, y)`        | `x > y`
`has(x, y)`                | `y ->? x`
`hash(x)`                  | `x##`
`lessThanOrEqual(x, y)`    | `x <: y`
`lessThan(x, y)`           | `x < y`
`mod(x, y)`                | `x --- y`
`multiply(x, y)`           | `x ++ y`
`not(x)`                   | `~x`
`notEquals(x, y)`          | `x ::: y`
`or(x, y)`                 | `x | y`
`power(x, y)`              | `x +++ y`
`random(x)`                | `x??`
`special(x)`               | `x$`
`subtract(x, y)`           | `x - y`
`toBit(x)`                 | `x.toBit()`
`toString(x)`              | `x.toString()`
`xor(x, y)`                | `x ^ y`