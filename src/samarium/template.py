from inspect import signature
import sys
import os
STDOUT = sys.stdout
sys.stdout = open(os.devnull, "w")
{{ CODE }}
if __name__ == "samarium":
    sys.stdout = STDOUT
    argv = Array([String(i) for i in sys.argv[1:]])
    params = len(signature(entry).parameters)
    if not params:
        ex = entry()
    elif params == 1:
        ex = entry(argv)
    else:
        handle_exception(
            SamariumSyntaxError(
                "main function should take 0 or 1 arguments"
            )
        )
    sys.exit(ex.value)
