# `string` module

The `string` module contains several useful functions for string manipulation, as well as some variables containing groups of similar characters.

Variable      | Contents
---           | ---
`UPPERCASE`   | `ABCDEFGHIJKLMNOPQRSTUVWXYZ`
`LOWERCASE`   | `abcdefghijklmnopqrstuvwxyz`
`LETTERS`     | `UPPERCASE + LOWERCASE`
`OCTDIGITS`   | `01234567`
`DIGITS`      | `0123456789`
`HEXDIGITS`   | `0123456789abcdef`
`PUNCTUATION` | ``!"#$%&'()*+,-./:;<=>?@[\]^_`{\|}~``
`WHITESPACE`  | `[space]\t\n\r\f\v`
`PRINTABLE`   | `LETTERS + DIGITS + PUNCTUATION + WHITESPACE`

Function                                                       | Use
---                                                            | ---
`center(string, length[, char])`[^1] | Returns `string` centered in a new string of length `length`, padded using the specified `char`.<br>If `char` is not specified, it defaults to `" "` (space).<br>`string` is returned unchanged if `length` is less than or equal to the length of `string`.
`starts_with(string, prefix)`                                   | Returns `1` if `string` starts with the substring `prefix`, otherwise returns `0`.
`ends_with(string, suffix)`                                     | Returns `1` if `string` ends with the substring `suffix`, otherwise returns `0`.
`split(string[, delimiter])`                                   | Returns an array of the words in `string`, separated by `delimiter`.<br>If `delimiter` is not specified, it defaults to `" "`.
`capitalize(string)`                                           | Returns a copy of `string` with the first character set to uppercase (assuming it's a cased character[^2]) and all subsequent character set to lowercase.
`title(string)`                                                | Returns a copy of `string` with the first character of each word (separated by spaces) set to uppercase (assuming they're cased characters[^2]), and all subsequent characters of each word set to lowercase.
`join(iterable[, delimiter])`                                  | Returns a string with each consecutive member of `iterable` converted to a string and joined with `delimiter` between them. If `delimiter` is not specified, it defaults to `" "`.
`strip_left(string, prefix)`                                    | Returns a copy of `string` with `prefix` removed from the beginning, multiple times if `string` still begins with `prefix`.<br>If `string` doesn't begin with `prefix`, a copy of the original `string` is returned.
`strip_right(string, suffix)`                                   | Returns a copy of `string` with `suffix` removed from the end, multiple times if `string` still ends with `suffix`.<br>If `string` doesn't end with `suffix`, a copy of the original `string` is returned.
`strip(string, chars)`                                         | Returns a copy of `string` with `chars` removed from both the beginning and end, as in `strip_left` and `strip_right`.
`is_wrapped(string, chars)`                                     | Returns `1` if `string` both starts and ends with the substring `chars`, otherwise returns `0`.
`to_lower(string)`                                              | Returns a copy of `string` with every cased character[^2] set to lowercase.
`to_upper(string)`                                              | Returns a copy of `string` with every cased character[^2] set to uppercase.
`swapcase(string)`                                             | Returns a copy of `string` with every cased character[^2] set to the opposite of its original case.
`leftpad(string, length[, char])`                              | Returns a copy of `string` padded on the left so that it's `length` characters long, using `char` for padding.<br>If `char` is not specified, it defaults to `" "`. If `length` is shorter than `string`'s length, a copy of `string` is returned.
`rightpad(string, length[, char])`                             | Returns a copy of `string` padded on the right so that it's `length` characters long, using `char` for padding.<br>If `char` is not specified, it defaults to `" "`. If `length` is shorter than `string`'s length, a copy of `string` is returned.
`is_upper(string)`                                              | Returns `1` if every cased character[^2] in `string` is uppercase, otherwise returns `0`.
`is_lower(string)`                                              | Returns `1` if every cased character[^2] in `string` is lowercase, otherwise returns `0`.
`is_title(string)`                                              | Returns `1` if `string` is in title case, i.e. matches the output of `title(string)` exactly.
`is_capitalized(string)`                                        | Returns `1` if `string` is capitalized, i.e. matches the output of `capitalize(string)` exactly.
`is_in_group(string, group)`                                     | Returns `1` if every character in `string` is in the specified `group` of type Array or String, otherwise returns `0`.
`is_alphabetic(string)`                                         | Returns `1` if every character in `string` is an alphabetic character, i.e. is contained in the string `letters`, otherwise returns `0`.
`is_alphanumeric(string)`                                       | Returns `1` if every character in `string` is an alphanumeric character, i.e. is contained in the strings `letters` or `numbers`, otherwise returns `0`.
`is_decimal(string)`                                            | Returns `1` if every character in `string` is a decimal digit, i.e. is contained in the string `DIGITS`, otherwise returns `0`.
`is_octal(string)`                                              | Returns `1` if every character in `string` is an octal digit, i.e. is contained in the string `OCTDIGITS`, otherwise returns `0`.
`is_hexadecimal(string)`                                        | Returns `1` if every character in `string` is a hexadecimal digit, i.e. is contained in the string `HEXDIGITS`, otherwise returns `0`.
`wrap(string, wrapper)`                                        | Returns a copy of `string` with `wrapper` added to the start and end.
`replace(string, replacement[, count])`                        | Returns a copy of `string`, with all instances of each key in the `replacement` table replaced with its corresponding value.<br>If `count` is specified, only the first `count` instances of each key will be replaced, starting from the left.
`format(string, fields)`                                       | Replaces field placeholders with supplied values, e.g.:<br>`format("Hi $name!", {{"name" -> "Bob"}}) :: "Hi Bob!"`<br>`format("$$age = $age", {{"age" -> /\\\\}}) :: "$age = 16"`

[^1]: An argument in `[square brackets]` means that it has a default value, and so it isn't necessary to give it a value.

[^2]: Cased characters are alphabetic characters in either uppercase or lowercase; `LETTERS` is a string of all cased characters.
