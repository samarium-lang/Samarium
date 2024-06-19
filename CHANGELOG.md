# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.2] - 2024-06-19

### Changed
- Session names now only allow a limited set of characters (`[a-zA-Z0-9_\-]`)

### Fixed
- `:session load` will no longer crash on a non-existent session

## [0.6.1] - 2024-06-18

### Changed
- Rewrote REPL config handling to not use the `configzen` library

## [0.6.0] - 2024-06-14

### Added
- `=>!` now accepts strings
- Added an exception note for `string.split`
- Allowed adding notes for `!!!`
- Command system for the REPL
- Data classes
- Function composition
- Made the semicolon optional for `!`, `!!!`, `*`, `**`
- `math.max` and `math.min` now work with varargs
- `String+`
- `-String`
- `~Table`
- The REPL now automatically displays most expressions

### Changed
- `String ++ -Number` now throws a type error (ambiguous operation)

### Fixed
- Fixed function conversion when `@export`ing
- Fixed internal name of `math.round`
- Fixed `math.sqrt` using an incorrect variable name
- Fixed multiline string handling in the REPL
- Fixed REPL quitting on syntax error
- `math.round` now correctly provides a default value for `ndigits`
- The transpiler now correctly disallows literals around identifiers
- `types.Boolean` should now correctly interract with external types
- Various minor fixes to the transpiler

## [0.5.3] - 2023-04-21

### Fixed
- Fixed entrypoint argc check template

## [0.5.2] - 2023-04-21

### Fixed
- Corrected `types.Number` type alias name

## [0.5.1] - 2023-04-08

### Added
- `~` is now equal to `-1` when not followed by a value (e.g. `~;` or `~<`, but
  not `~x` or `~/\`)

### Fixed
- Implicit null is no longer placed before `~` (meaning that `>~<` is no longer
  invalid syntax)

## [0.5.0] - 2023-04-02

### Added
- `collections.Queue` now supports membership checking
- `collections.Set` now uses the built-in set-based Array operations (working
  with small sets can be up to 3,600x faster)
- Files are now iterable
- `iter.filter` and `iter.map` now adapt to functions based on their number of
  parameters
- `math.is_int`
- `math.ceil`
- `math.floor`
- `math.round`
- `math.to_bin` (to replace `Integer$`)
- Number type (in place of the Integer type):
  - supports floats
  - `x$` now floors the number
  - `x -- y` now does true division rather than floor division
- Number literals, using `` ` `` as the decimal point (meaning that it's no
  longer ignored by the tokenizer)
- Nulls can now be cast to Numbers
- Parallel assignment
- `random.sample` now supports slices
- Set-based Array operations:
  - `-x` returns a copy of `x` with duplicates removed
  - `x -- y` ("difference") tries removing elements of `y` from `x`, even if
    they're not present
  - `x --- y` removes all duplicates of `y` in `x`
  - `x | y` ("union") creates an array with elements that appear in either `x`
    or `y` (duplicates possible)
  - `x & y` ("intersection") creates an array with elements that appear in both
    `x` and `y` (duplicates possible)
  - `x ^ y` ("symmetric difference") creates an array with elements that appear
    in either `x` or `y`, but not both (duplicates possible)
- Slices are now hashable
- `String -- String` (old `String - String` behavior)
- `String++` (equivalent to `String ++ /\`)
- `string.split` now accepts multiple separators
- String→Number now supports scientific notation
- `string.split_lines`
- Strings can have their characters shifted by adding or subtracting Integers
- `types.Frozen`

### Changed
- Flipped argument order for `iter.reduce`
- Improved Array/Slice/String index typechecking
- Improved CLI error messages
- Improved error messages
- Improved `File.__str__`
- Improved implicit null detection
- Improved slice transpilation
- `random.shuffle` now does type checking againast slices
- `String - String` now removes only the first occurence
- The main function is no longer required
- Two or more consecutive logical NOTs are now considered a syntax error

### Fixed
- Comments are now correctly tokenized
- Fixed `...` special method not being detected
- Fixed Slice→Array construction
- Fixed some yield statements crashing the transpiler
- Functions are now correctly displayed in Arrays/Tables
- Logical NOT (`~~`) no longer lets Python's `bool` slip in
- Multiline strings are now correctly tokenized
- `Number ++ String` is no longer detected as an invalid operation
- Slices are now correctly detected as objects directly after scope exit
- `String.__repr__` now correctly handles escape sequences
- `Type(a) != B` no longer yields incorrect results
- `UserAttrs` can no longer show up when using `x!?`
- Varargs functions now work correctly with recursive functions and decorators

### Removed
- `collections.StaticArray`
- Integer type

<br>

The [Examples](https://samarium-lang.github.io/Samarium/examples/) page was also
updated with new examples.

Thanks to [@DancingGrumpyCat](https://github.com/DancingGrumpyCat) for improving the documentation!

## [0.4.0] - 2022-12-01

### Added
- `Array%`
- `Enum%`
- `io` module:
  - `io.Bytes`
  - `io.inputcast`
  - `io.read_until`
- `iter.cycle` by [@Lunarmagpie](https://github.com/Lunarmagpie)
- New import system, including:
  - import aliases
  - inline imports
- New special method syntax
- Partial Python Interoperability by [@Endercheif](https://github.com/Endercheif)
- `start` parameter for `math.sum`, thus allowing to sum non-Integers
- Static methods (`~'*` keyword)
- `string.ordinal`
- `string.split()` now supports separators of length greater than 1, and also handles empty separators
- Strings of length greater than 1 can now be cast into Arrays of Integers
- Subtracting strings
- Support for `^L`, `^[[A`, `^[[B`, `^[[C`, `^[[D` in the REPL
- `to_bit` methods for:
  - `Enum`
  - `File`
  - `Iterator`
  - `Module`
- `Type`s and functions are now hashable
- Zip `><` operator
- `Zip` type

### Changed
- Flipped argument order for:
  - `iter.map`
  - `iter.filter`
  - `iter.filter_false`
- Greatly improved error messages
- Improved `collections.Set` methods:
  - Replaced `union` with `|`
  - Replaced `intersection` with `&`
  - Replaced `difference` with `-`
  - Removed `is_subset` in place of `::`, `:::`, `>`, `<`, `>:`, `<:` operator support
- Improved function to string conversion
- Improved implicit null detection
- Improved readline error handling
- Improved slice object detection
- Improved string integer parsing
- Improved variable type verification
- Rewrote the objects (should be 10–50% faster than Samarium 0.3.1 🚀)
- Replaced the native tokenizer with a [crossandra](https://github.com/trag1c/crossandra) tokenizer (~3x faster tokenization 🚀)
- Updated `to_string` methods of:
  - `collections.ArithmeticArray`
  - `collections.Deque`
  - `collections.Queue`
  - `collections.Set`

### Fixed
- `collections.Set.#new_set_size` now takes unsized sets into consideration
- Constructing `Slice`s from `Type` now correctly works
- Error message shown when trying to run an unknown file is now written to stderr, not stdout
- Syntax errors now cannot be caught

### Removed
- `collections.Set.values()` (use `collections.Set.items`)
- English special method names
- `iter.zip` (use the `><` operator)
- `iter.enumerate` (use the `><` operator with `<<>>`)
- Some dead code :)
- `string.format` (use `String`'s `---` operator)

---

Also big thanks to [@qexat](https://github.com/qexat) & [@Celeo](https://github.com/Celeo) for code improvements! ❤️

## [0.3.1] - 2022-09-23

### Fixed
- Added missing cases for implicit null

### Removed
- Unused imports & variables in the standard library
- Unused slots in built-in types


## [0.3.0] - 2022-09-21

### Added
- `**` (the yield statement)
- Array support for `string.format`
- Better error messages
- `datetime` module by [@Endercheif](https://github.com/Endercheif)
- Enums
- `iter.chunks`
- `iter.flatten`
- `iter.sorted`
- Iterators
- Memory address lookup
- Private variables
- snake_case support
- Substring support for `iter.find_all`

### Changed
- `#` for assert has been replaced by `!!`
- `@@` now returns the Unix timestamp
- `@@@` now returns the date and time array
- Classes can now be used as entry points
- Improved hashing speed
- Improved `iter` module speed by making it use Iterators over Arrays
- Moved from [termcolor](https://pypi.org/project/termcolor/) to [Dahlia](https://github.com/trag1c/Dahlia)
- Rewrote the transpiler
- Slice objects are now iterable and can be used as ranges (about 3–7x faster than `iter.range` 🚀)
- Slices now use `..` instead of `**` for the step delimiter (`<<x..y**z>>` would be `<<x..y..z>>`)
- Class special method names were changed to snake_case
- Standard Library function names were changed to snake_case
- Standard Library constant names were changed to SCREAMING_SNAKE_CASE
- `to_string` method doesn't need to be defined for the object to be printable (defaults to `<ClassName@MemoryAddress>`)

### Fixed
- Nested slicing

### Removed
- `_` as a null token
- `iter.range` (use slices)
- `iter.sort` (use `iter.sorted`)


## [0.2.3] - 2022-06-20

### Fixed
- Fixed converting slices to strings


## [0.2.2] - 2022-06-18

### Fixed
- Added a missing `argc` attribute for the template


## [0.2.1] - 2022-06-18

### Fixed
- Class methods now correctly pass the instance


## [0.2.0] - 2022-06-13

### Added
- `-h` / `--help` option
- Argument unpacking
- Decorators
- Enriched modules:
  - `collections.ArithmeticArray`
  - `iter`:
    - `all`
    - `any`
    - `findAll`
    - `pairwise`
    - `zip`
    - `zipLongest`
  - `math.isPrime`
  - `random.randint`
  - `string.format`
  - `types`:
    - `Array`
    - `Integer`
    - `Null`
    - `Slice`
    - `String`
    - `Table`
    - `UUID4`
- File descriptor support for standard stream access
- Greatly improved object constructors for:
  - `Array`:
    - Default value: `[]`
    - `Array(a)` will now return a copy of the array `a`
    - Arrays can now be constructed from strings and tables:
      - `Array("ball") :: ["b", "a", "l", "l"]`
      - `Array({{// -> /\\/, "X" -> "D"}}) :: [[//, /\\/], ["X", "D"]]`
  - `Integer`:
    - Default value: `\`
    - Added support for binary, octal, hexadecimal representations:
      - `Integer("b:1000") :: Integer("8")`
      - `Integer("o:1000") :: Integer("512")`
      - `Integer("x:1000") :: Integer("4096")`
  - `String`:
    - Default value: `""`
    - `String(s)` will now return a copy of the string `s`
  - `Table`:
    - Default value: `{{}}`
    - `Table(t)` will now return a copy of the table `t`
    - Tables can be constructed from arrays containing 2-element iterables:
      - `Table([[//, /\\/], "XD"]) :: {{// -> /\\/, "X" -> "D"}}`
- Introduced a new `Function` class for functions, replacing the old decorator
- New function syntax:
  - `arg?` now makes the argument optional
  - optional arguments require setting the default value using the `arg <> default` statement inside the function body
  - `args...` will now accept a variable number of arguments and pass them to the function as an array
- New `operator` module - containing standard operators as functions:
  - `add` (`x + y`)
  - `and` (`x & y`)
  - `cast` (`x%`)
  - `divide` (`x -- y`)
  - `equals` (`x :: y`)
  - `greaterThanOrEqual` (`x >: y`)
  - `greaterThan` (`x > y`)
  - `has` (`y ->? x`)
  - `hash` (`x##`)
  - `lessThanOrEqual` (`x <: y`)
  - `lessThan` (`x < y`)
  - `mod` (`x --- y`)
  - `multiplty` (`x ++ y`)
  - `not` (`~x`)
  - `notEquals` (`x ::: y`)
  - `or` (`x | y`)
  - `power` (`x +++ y`)
  - `random` (`x??`)
  - `special` (`x$`)
  - `subtract` (`x - y`)
  - `toBit`
  - `toString`
  - `xor` (`x ^ y`)
- Project description in `pyproject.toml`
- Samarium REPL
- Separate error for IO operations: `IOError`
- Some objects now have a `.random` method, supported by the `object??` syntax:
  - `array??` will return a random element
  - `integer??` will return:
    - a number in range `[0, n)` for positive values
    - a number in range `[n, 0)` for negative values
    - `0` for `0??`
  - `slice??` will return a number from an attribute-based range
  - `string??` will return a random character
  - `table??` will return a random key
- Shebang support
- Special method for functions:
  - `function$` will now return the number of parameters the function accepts
- While loop condition is now optional (`.. {}` is equivalent to `.. / {}`)

### Changed
- `<>` now serves for setting the default parameter value 
- Bumped the minimum Python version to 3.9
- Classes no longer need the `create` method defined to be initializable.
- Improved scopes and empty body handling
- Improved and added new error messages, such as:
  - Invalid table keys
  - Unbalanced brackets
  - Too many parameters for the main function (or the lack of one)
- Improved object speed:
  - `Array`s — up to 30% faster
  - `Integer`s — up to 2.4x faster
  - `Null` objects — up to 2.2x faster
  - `String`s — up to 40% faster
  - `Table`s — up to 25% faster
- Improved transpiling safety
- Improved internal typechecking accuracy
- RNG syntax (`^^x -> y^^`) was replaced by the new random `object??` syntax
- `Slice`s can now be instantiated as standalone objects
- Various refactorings

### Fixed
- Fixed `-c` option not tokenizing some statements properly, such as:
  - statements starting with a table definition
  - statements ending with a `!`
- Fixed `string.join` for empty delimiters
- Fixed `string.pad` doubling when `string$` was equal to `length`
- Fixed exception name categorization
- Fixed `string.replace`
- Functions defined inside class methods no longer need an instance
- Fixed false positives for multiple type verification
- Fixed Integer construction for cross-type comparison

### Removed
- `->` operator support for assert (`#`)
- Constants
- Default parameter value in the function definition
- `math.fromDecimal` - use `types.Integer(string)` instead
- `random.choice` - use `iterable??` instead


## [0.1.0] - 2022-03-05

Initial release 🚀

[0.1.0]: https://github.com/samarium-lang/Samarium/releases/tag/0.1.0
[0.2.0]: https://github.com/samarium-lang/Samarium/compare/0.1.0...0.2.0
[0.2.1]: https://github.com/samarium-lang/Samarium/compare/0.2.0...0.2.1
[0.2.2]: https://github.com/samarium-lang/Samarium/compare/0.2.1...0.2.2
[0.2.3]: https://github.com/samarium-lang/Samarium/compare/0.2.2...0.2.3
[0.3.0]: https://github.com/samarium-lang/Samarium/compare/0.2.3...0.3.0
[0.3.1]: https://github.com/samarium-lang/Samarium/compare/0.3.0...0.3.1
[0.4.0]: https://github.com/samarium-lang/Samarium/compare/0.3.1...0.4.0
[0.5.0]: https://github.com/samarium-lang/Samarium/compare/0.4.0...0.5.0
[0.5.1]: https://github.com/samarium-lang/Samarium/compare/0.5.0...0.5.1
[0.5.2]: https://github.com/samarium-lang/Samarium/compare/0.5.1...0.5.2
[0.5.3]: https://github.com/samarium-lang/Samarium/compare/0.5.2...0.5.3
[0.6.0]: https://github.com/samarium-lang/Samarium/compare/0.5.3...0.6.0
[0.6.1]: https://github.com/samarium-lang/Samarium/compare/0.6.0...0.6.1
[0.6.2]: https://github.com/samarium-lang/Samarium/compare/0.6.1...0.6.2
