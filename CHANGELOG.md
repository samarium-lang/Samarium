# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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