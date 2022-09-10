# `string` module

The `string` module contains several useful functions for string manipulation, as well as some variables containing groups of similar characters.

Variable      | Contents
---           | ---
`DIGITS`      | `0123456789`
`HEXDIGITS`   | `0123456789abcdef`
`LETTERS`     | `UPPERCASE + LOWERCASE`
`LOWERCASE`   | `abcdefghijklmnopqrstuvwxyz`
`OCTDIGITS`   | `01234567`
`PRINTABLE`   | `LETTERS + DIGITS + PUNCTUATION + WHITESPACE`
`PUNCTUATION` | ``!"#$%&'()*+,-./:;<=>?@[\]^_`{\|}~``
`UPPERCASE`   | `ABCDEFGHIJKLMNOPQRSTUVWXYZ`
`WHITESPACE`  | `[space]\t\n\r\f\v`

Function                                 | Use
---                                      | ---
`capitalize(string)`                     | Returns a copy of `string` with the first character set to uppercase (assuming it's a cased character[^2]) and all subsequent character set to lowercase.
`center(string, length[, char])`[^1]     | Returns `string` centered in a new string of length `length`, padded using the specified `char`.<br>If `char` is not specified, it defaults to `" "` (space).<br>`string` is returned unchanged if `length` is less than or equal to the length of `string`.
`ends_with(string, suffix)`              | Returns `1` if `string` ends with the substring `suffix`, otherwise returns `0`.
`format(string, fields)`                 | Replaces field placeholders with supplied values, e.g.:<br>`format("Hi $name!", {{"name" -> "Bob"}}) :: "Hi Bob!"`<br>`format("$$age = $age", {{"age" -> /\\\\}}) :: "$age = 16"`
`is_alphabetic(string)`                  | Returns `1` if every character in `string` is an alphabetic character, i.e. is contained in the string `letters`, otherwise returns `0`.
`is_alphanumeric(string)`                | Returns `1` if every character in `string` is an alphanumeric character, i.e. is contained in the strings `letters` or `numbers`, otherwise returns `0`.
`is_capitalized(string)`                 | Returns `1` if `string` is capitalized, i.e. matches the output of `capitalize(string)` exactly.
`is_decimal(string)`                     | Returns `1` if every character in `string` is a decimal digit, i.e. is contained in the string `DIGITS`, otherwise returns `0`.
`is_hexadecimal(string)`                 | Returns `1` if every character in `string` is a hexadecimal digit, i.e. is contained in the string `HEXDIGITS`, otherwise returns `0`.
`is_in_group(string, group)`             | Returns `1` if every character in `string` is in the specified `group` of type Array or String, otherwise returns `0`.
`is_lower(string)`                       | Returns `1` if every cased character[^2] in `string` is lowercase, otherwise returns `0`.
`is_octal(string)`                       | Returns `1` if every character in `string` is an octal digit, i.e. is contained in the string `OCTDIGITS`, otherwise returns `0`.
`is_title(string)`                       | Returns `1` if `string` is in title case, i.e. matches the output of `title(string)` exactly.
`is_upper(string)`                       | Returns `1` if every cased character[^2] in `string` is uppercase, otherwise returns `0`.
`is_wrapped(string, chars)`              | Returns `1` if `string` both starts and ends with the substring `chars`, otherwise returns `0`.
`join(iterable[, delimiter])`            | Returns a string with each consecutive member of `iterable` converted to a string and joined with `delimiter` between them. If `delimiter` is not specified, it defaults to `" "`.
`leftpad(string, length[, char])`        | Returns a copy of `string` padded on the left so that it's `length` characters long, using `char` for padding.<br>If `char` is not specified, it defaults to `" "`. If `length` is shorter than `string`'s length, a copy of `string` is returned.
`replace(string, replacement[, count])`  | Returns a copy of `string`, with all instances of each key in the `replacement` table replaced with its corresponding value.<br>If `count` is specified, only the first `count` instances of each key will be replaced, starting from the left.
`rightpad(string, length[, char])`       | Returns a copy of `string` padded on the right so that it's `length` characters long, using `char` for padding.<br>If `char` is not specified, it defaults to `" "`. If `length` is shorter than `string`'s length, a copy of `string` is returned.
`split(string[, delimiter])`             | Returns an array of the words in `string`, separated by `delimiter`.<br>If `delimiter` is not specified, it defaults to `" "`.
`starts_with(string, prefix)`            | Returns `1` if `string` starts with the substring `prefix`, otherwise returns `0`.
`strip(string, chars)`                   | Returns a copy of `string` with `chars` removed from both the beginning and end, as in `strip_left` and `strip_right`.
`strip_left(string, prefix)`             | Returns a copy of `string` with `prefix` removed from the beginning, multiple times if `string` still begins with `prefix`.<br>If `string` doesn't begin with `prefix`, a copy of the original `string` is returned.
`strip_right(string, suffix)`            | Returns a copy of `string` with `suffix` removed from the end, multiple times if `string` still ends with `suffix`.<br>If `string` doesn't end with `suffix`, a copy of the original `string` is returned.
`swapcase(string)`                       | Returns a copy of `string` with every cased character[^2] set to the opposite of its original case.
`title(string)`                          | Returns a copy of `string` with the first character of each word (separated by spaces) set to uppercase (assuming they're cased characters[^2]), and all subsequent characters of each word set to lowercase.
`to_lower(string)`                       | Returns a copy of `string` with every cased character[^2] set to lowercase.
`to_upper(string)`                       | Returns a copy of `string` with every cased character[^2] set to uppercase.
`wrap(string, wrapper)`                  | Returns a copy of `string` with `wrapper` added to the start and end.

[^1]: An argument in `[square brackets]` means that it has a default value, and so it isn't necessary to give it a value.

[^2]: Cased characters are alphabetic characters in either uppercase or lowercase; `LETTERS` is a string of all cased characters.
