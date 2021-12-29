**1. Write docs**
> As I've said, I want them to be user friendly, chill and not super serious, so it's really just describing the features in a simple way

**2. Fix the extension**
> Currently there are 3 things to fix: <br>→ Class with parents on separate lines <br>→ Function with parameters on separate lines <br>→ Function when default arguments are used

**3. Implement Standard Library**
> This is simply writing and testing Samarium code for all functions there are to do + your own suggestions

**4. Object Oriented Stuff**
> This includes coming up with names for special methods which support syntactic sugar + finally decide on `SMInteger.__special__`

**5. Slicing Prototype**
> This includes creating a concept for its syntax, and also coming up with a way to parse it in a way which will not allow creating Python lists. Let's say the syntax is `myArray_\ -> /\_;`, then if I were to parse it as `myArray[0:2]` then using just `_/_` would get parsed to `[1]`, which would result in a Python `list`. Therefore this would require working with `__getitem__`, `__getslice__`, `__setitem__`, and `__setslice__`, where the latter two would require some nice workaround to parse `myArray_/_ : //` as `myArray.__setitem__(1, 3)`

**6. SMNull Wrapper**
> Make the parser decorate every function in a wrapper which returns an SMNull object if the function returns None

**7. Detect genexprs**
> This is a bit tricky, but it's not that hard. The only way to do this is to use a regex to find the genexpr syntax, and then throw a syntax error if it's found.

**8. Fix single-line comment parsing**
> This can only by done by including `\n` as a token again.

**9. Fix code execution in comments**
> Parser doesn't ignore the contents of comments, so it still tries to call built-in functions like `!` or `!!!`.

**10. Fix `_throw` including the indentation**
> When calling `!!!` (maybe `!` too, didn't test), it wraps the entire line including the indentation, thus causing an IndentationError when transpiled to Python.

**11. Test stdlib**
> Test all functions in the standard library, and make sure they work as expected.

**12. Test casting**
> `%` after `SMInteger` or `SMString` types should convert them just as Python's `ord` and `chr` would.

**13. Feature concepts**
> There are still 2 unused characters, `` ` `` and `_` + some combination of characters could be used as well, so we could add some stuff to the language.

**14. `}` parsing**
> Currently, `}` is the only character (that I'm aware of) that both:
> <br>→ can be the last character of a valid program
> <br>→ has multiple meanings (either `}` for `BRACE_CLOSE` or `}}` for `TABLE_CLOSE`)
> <br>When `}` is the last character of a file (as in there's no newline or anything, literally the last character), an IndexError occurs when the tokenizer tries to check if the next character is also `}`.