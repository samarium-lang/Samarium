[Back to Table of Contents](../README.md#table-of-contents)

# `string` module

The `string` module contains several useful functions for string manipulation, as well as some variables containing groups of similar characters.

Variable      | Contents
---           | ---
`uppercase`   | `ABCDEFGHIJKLMNOPQRSTUVWXYZ`
`lowercase`   | `abcdefghijklmnopqrstuvwxyz`
`letters`     | `uppercase + lowercase`
`octdigits`   | `01234567`
`digits`      | `0123456789`
`hexdigits`   | `0123456789abcdef`
`punctuation` | ``!"#$%&'()*+,-./:;<=>?@[\]^_`{\|}~``
`whitespace`  | `[space]\t\n\r\f\v`
`printable`   | `letters + digits + punctuation + whitespace`

Function                                                       | Use
---                                                            | ---
`center(string, length[, char])`[<sup>a</sup>](#note-a) | Returns `string` centered in a new string of length `length`, padded using the specified `char`. If `char` is not specified, it defaults to `" "` (space). `string` is returned unchanged if `length` is less than or equal to the length of `string`.
`startsWith(string, prefix)`                                   | Returns `1` if `string` starts with the substring `prefix`, otherwise returns `0`.
`endsWith(string, suffix)`                                     | Returns `1` if `string` ends with the substring `suffix`, otherwise returns `0`.
`split(string[, delimiter])`                                   | Returns an array of the words in `string`, separated by `delimiter`. If `delimiter` is not specified, it defaults to `" "`.
`capitalize(string)`                                           | Returns a copy of `string` with the first character set to uppercase (assuming it's a cased character[<sup>b</sup>](#note-b)) and all subsequent character set to lowercase.
`title(string)`                                                | Returns a copy of `string` with the first character of each word (separated by spaces) set to uppercase (assuming they're cased characters[<sup>b</sup>](#note-b)), and all subsequent characters of each word set to lowercase.
`join(iterable[, delimiter])`                                  | Returns a string with each consecutive member of `iterable` converted to a string and joined with `delimiter` between them. If `delimiter` is not specified, it defaults to `" "`.
`stripLeft(string, prefix)`                                    | Returns a copy of `string` with `prefix` removed from the beginning, multiple times if `string` still begins with `prefix`. If `string` doesn't begin with `prefix`, a copy of the original `string` is returned.
`stripRight(string, suffix)`                                   | Returns a copy of `string` with `suffix` removed from the end, multiple times if `string` still ends with `suffix`. If `string` doesn't end with `suffix`, a copy of the original `string` is returned.
`strip(string, chars)`                                         | Returns a copy of `string` with `chars` removed from both the beginning and end, as in `stripLeft` and `stripRight`.
`isWrapped(string, chars)`                                     | Returns `1` if `string` both starts and ends with the substring `chars`, otherwise returns `0`.
`toLower(string)`                                              | Returns a copy of `string` with every cased character[<sup>b</sup>](#note-b) set to lowercase.
`toUpper(string)`                                              | Returns a copy of `string` with every cased character[<sup>b</sup>](#note-b) set to uppercase.
`swapcase(string)`                                             | Returns a copy of `string` with every cased character[<sup>b</sup>](#note-b) set to the opposite of its original case.
`leftpad(string, length[, char])`                              | Returns a copy of `string` padded on the left so that it's `length` characters long, using `char` for padding. If `char` is not specified, it defaults to `" "`. If `length` is shorter than `string`'s length, a copy of `string` is returned.
`rightpad(string, length[, char])`                             | Returns a copy of `string` padded on the right so that it's `length` characters long, using `char` for padding. If `char` is not specified, it defaults to `" "`. If `length` is shorter than `string`'s length, a copy of `string` is returned.
`isUpper(string)`                                              | Returns `1` if every cased character[<sup>b</sup>](#note-b) in `string` is uppercase, otherwise returns `0`.
`isLower(string)`                                              | Returns `1` if every cased character[<sup>b</sup>](#note-b) in `string` is lowercase, otherwise returns `0`.
`isTitle(string)`                                              | Returns `1` if `string` is in title case, i.e. matches the output of `title(string)` exactly.
`isCapitalized(string)`                                        | Returns `1` if `string` is capitalized, i.e. matches the output of `capitalize(string)` exactly.
`isInGroup(string, group)`                                     | Returns `1` if every character in `string` is in the specified `group` of type Array or String, otherwise returns `0`.
`isAlphabetic(string)`                                         | Returns `1` if every character in `string` is an alphabetic character, i.e. is contained in the string `letters`, otherwise returns `0`.
`isAlphanumeric(string)`                                       | Returns `1` if every character in `string` is an alphanumeric character, i.e. is contained in the strings `letters` or `numbers`, otherwise returns `0`.
`isDecimal(string)`                                            | Returns `1` if every character in `string` is a decimal digit, i.e. is contained in the string `digits`, otherwise returns `0`.
`isOctal(string)`                                              | Returns `1` if every character in `string` is an octal digit, i.e. is contained in the string `octdigits`, otherwise returns `0`.
`isHexadecimal(string)`                                        | Returns `1` if every character in `string` is a hexadecimal digit, i.e. is contained in the string `hexdigits`, otherwise returns `0`.
`wrap(string, wrapper)`                                        | Returns a copy of `string` with `wrapper` added to the start and end.
`replace(string, replacement[, count])`                        | Returns a copy of `string`, with all instances of each key in the `replacement` table replaced with its corresponding value.[<sup>c</sup>](#note-c) If `count` is specified, only the first `count` instances of each key will be replaced, starting from the left.

<sup id="note-a">a</sup> An argument in `[square brackets]` means that it has a default value, and so it isn't necessary to give it a value.

<sup id="note-b">b</sup> Cased characters are alphabetic characters in either uppercase or lowercase; `letters` is a string of all cased characters.

<sup id="note-c">c</sup> A bug exists in `string.replace` in Samarium v0.1.0, in that if a substring is to be replaced by another substring that contains itself, for example `{{"a" -> "aa"}}`, an infinite loop will be entered.
