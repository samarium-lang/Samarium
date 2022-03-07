from inspect import signature
import sys
import os
STDOUT = sys.stdout
sys.stdout = open(os.devnull, "w")
{{ CODE }}
if __name__ == "samarium":
    sys.stdout = STDOUT
    argv = Array([String(i) for i in sys.argv[1:]])
    if len(signature(entry).parameters) > 1:
        handle_exception(
            SamariumSyntaxError(
                "main function should take 0 or 1 arguments"
            )
        )
    try:
        ex = entry(argv)
    except TypeError:
        ex = entry()
    sys.exit(ex.value)
