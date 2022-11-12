# `operator` module

This module contains a set of functions corresponding to the native operators of Samarium. For instance, `operator.mul(a, b)` is equivalent to `a ++ b`. Each of the function names can be used for defining special methods in classes.

<center>

Function       | Operator
---            | :---:
`add(x, y)`    | `x + y`
`and(x, y)`    | `x & y`
`cast(x)`      | `x%`
`div(x, y)`    | `x -- y`
`eq(x, y)`     | `x :: y`
`ge(x, y)`     | `x >: y`
`gt(x, y)`     | `x > y`
`has(x, y)`    | `y ->? x`
`hash(x)`      | `x##`
`le(x, y)`     | `x <: y`
`lt(x, y)`     | `x < y`
`mod(x, y)`    | `x --- y`
`mul(x, y)`    | `x ++ y`
`not(x)`       | `~x`
`ne(x, y)`     | `x ::: y`
`or(x, y)`     | `x | y`
`pow(x, y)`    | `x +++ y`
`random(x)`    | `x??`
`special(x)`   | `x$`
`sub(x, y)`    | `x - y`
`to_bit(x)`    | `/ ? x ,, \`
`to_string(x)` | `""?!(x)`
`xor(x, y)`    | `x ^ y`

</center>
