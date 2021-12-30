**1. Write docs**
> As I've said, I want them to be user friendly, chill and not super serious, so it's really just describing the features in a simple way

**2. Fix the extension**
> Currently there are 3 things to fix: <br>→ Class with parents on separate lines <br>→ Function with parameters on separate lines <br>→ Function when default arguments are used <br>→ The first argument in a lambda is highlighted like a function name

**3. Implement Standard Library**
> This is simply writing and testing Samarium code for all functions there are to do + your own suggestions

**4. Object Oriented Stuff**
> This includes coming up with names for special methods which support syntactic sugar + finally decide on `SMInteger.__special__`

**5. Slicing Prototype**
> This includes creating a concept for its syntax, and also coming up with a way to parse it in a way which will not allow creating Python lists. Let's say the syntax is `myArray_\ -> /\_;`, then if I were to parse it as `myArray[0:2]` then using just `_/_` would get parsed to `[1]`, which would result in a Python `list`. Therefore this would require working with `__getitem__`, `__getslice__`, `__setitem__`, and `__setslice__`, where the latter two would require some nice workaround to parse `myArray_/_ : //` as `myArray.__setitem__(1, 3)`

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

**13. Feature concepts**
> There are still 2 unused characters, `` ` `` and `_` + some combination of characters could be used as well, so we could add some stuff to the language.

**14. `}` parsing**
> Currently, `}` is the only character (that I'm aware of) that both:
> <br>→ can be the last character of a valid program
> <br>→ has multiple meanings (either `}` for `BRACE_CLOSE` or `}}` for `TABLE_CLOSE`)
> <br>When `}` is the last character of a file (as in there's no newline or anything, literally the last character), an IndexError occurs when the tokenizer tries to check if the next character is also `}`.

**15. SMArray.toString**
> This one is easy, simply it should wrap every string in `"` but since it returns a printable representation of the string, they're being removed.

**16. Empty functions**
> Make the parser add a `pass` inside empty Samarium functions when transpiling to Python.

**17. `SMNull` wrapper for lambdas**
> Working concepts I made, except I'm not really sure how one would add it to the parser:
> ```py
> # v1 : 169ns ± 0.234ns
> lambda: SMNull if (x := lambda_goes_here)() is None else x()
> # v2 : 123 ns ± 0.072ns
> lambda: SMNull if (x := (lambda_goes_here)()) is None else x

**18. Incorrect tokenizing without spacing**
> In the following example you can see how different the token is depending on the spacing:
> ```bash
> ...e->?array{e!;}
> # for e_-array_:
> #     print(e_);
> ...e ->?array{e!;}
> # for e_ in array_:
> #     print(e_);
> ```