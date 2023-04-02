!!! note
    The following guide assumes that you are familiar with the basics of
    programming.

# Numbers

Numbers are represented in base 2, using slashes and backslashes to represent 1
and 0 respectively. `` ` `` is used for the decimal point.
Negative numbers are represented as normal, with a `-` sign before them.

Let's see some examples of numbers:

Base 10  | Base 2    | Samarium
---      | ---       | ---
`0`      | `0`       | `\`
`0.5`    | `0.1`     | ``\`/``
`1`      | `1`       | `/`
`2`      | `10`      | `/\`
`2.3125` | `10.0101` | ``/\`\/\/``
`3`      | `11`      | `//`
`5`      | `101`     | `/\/`
`8`      | `1000`    | `/\\\`
`13`     | `1101`    | `//\/`
`21`     | `10101`   | `/\/\/`

Both the integer and decimal part of a number are optional, therefore:
> ``/` `` is equivalent to ``/`\``  
> `` `/`` is equivalent to ``\`/``  
> `` ` `` is equivalent to ``\`\``

Integers can be cast to characters represented by that integer's unicode code
point:

> `/\\\\/%` returns `"!"`  
> `//////%` returns `"?"`