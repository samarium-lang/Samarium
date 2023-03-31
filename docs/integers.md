!!! note
    The following guide assumes that you are familiar with the basics of
    programming.

# Integers

Integers are represented in base 2, using slashes and backslashes to represent 1
and 0 respectively.
Integers are the only type of number supported in Samarium.
Negative integers are represented as normal, with a `-` sign before them.

Let's see some examples of integers:

Base 10 | Base 2  | Samarium
---     | ---     | ---
`0`     | `0`     | `\`
`1`     | `1`     | `/`
`2`     | `10`    | `/\`
`3`     | `11`    | `//`
`5`     | `101`   | `/\/`
`8`     | `1000`  | `/\\\`
`13`    | `1101`  | `//\/`
`21`    | `10101` | `/\/\/`

Since Samarium is transpiled to Python, there's no limit to how large an integer
can be:

```sm
//\\/\\//////\\\\///\\////\\/\\/\\\\\\/////\\\\\\\\/////\\//\\/\\////\\////////\\////\\///\\\\\\\\//\\\\//\\///\\/\\\\\\/\\////\\//\\\\/\\\\/\\////\\/////\\/\\\\/\\\\\\\\\\//\\\\\\//\\\\/\\/\\\\//\\\\\\///\\/\\\\\\/\\\\\\/\\\\///\\//\\\\/\\\\//\\\\///\\//\\\\\\\\\\\\////////////////////////////////////////////////////////////////////////////////
```

Or in base 10:

```py
99999999999999999999999999999999999999999999999999999999999999999999999999999999
```

Integers can be casted to characters represented by that integer's unicode code
point:

> `/\\\\/%` returns `"!"`.

> `//////%` returns `"?"`.