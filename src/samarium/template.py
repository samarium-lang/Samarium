from inspect import signature
import sys
import os
STDOUT = sys.stdout
sys.stdout = open(os.devnull, "w")
{{ CODE }}
if __name__ == "samarium":
    sys.stdout = STDOUT
    if not entry.argc:
        ex = entry()
    elif entry.argc == 1:
        ex = entry(Array(map(String, sys.argv[1:])))
    else:
        raise SamariumSyntaxError("main function should take 0 or 1 arguments")
    sys.exit(ex.value)
