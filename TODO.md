**1. Write docs**
> As I've said, I want them to be user friendly, chill and not super serious, so it's really just describing the features in a simple way

**2. Fix the extension**
> Currently there are 3 things to fix: <br>→ Class with parents on separate lines <br>→ Function with parameters on separate lines <br>→ Function when default arguments are used <br>→ The first argument in a lambda is highlighted like a function name

**3. Implement Standard Library**
> This is simply writing and testing Samarium code for all functions there are to do + your own suggestions

**5. Slicing Prototype**
> This includes creating a concept for its syntax, and also coming up with a way to parse it in a way which will not allow creating Python lists. Let's say the syntax is `myArray_\ -> /\_;`, then if I were to parse it as `myArray[0:2]` then using just `_/_` would get parsed to `[1]`, which would result in a Python `list`. Therefore this would require working with `__getitem__`, `__getslice__`, `__setitem__`, and `__setslice__`, where the latter two would require some nice workaround to parse `myArray_/_ : //` as `myArray.__setitem__(1, 3)`

**7. Detect genexprs**
> This is a bit tricky, but it's not that hard. The only way to do this is to use a regex to find the genexpr syntax, and then throw a syntax error if it's found.

**17. `SMNull` wrapper for lambdas**
> Working concepts I made, except I'm not really sure how one would add it to the parser:
> ```py
> # v1 : 169ns ± 0.234ns
> lambda: SMNull if (x := lambda_goes_here)() is None else x()
> # v2 : 123 ns ± 0.072ns
> lambda: SMNull if (x := (lambda_goes_here)()) is None else x
> ```