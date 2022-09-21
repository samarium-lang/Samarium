from inspect import signature
import sys
import os
STDOUT = sys.stdout
sys.stdout = open(os.devnull, "w")
{{ CODE }}
if __name__ == "samarium":
    sys.stdout = STDOUT
    argc = entry.argc
    is_class = isinstance(entry, type)
    if is_class:
        argc.value -= 1
    if not argc:
        ex = entry()
    elif argc.value == 1:
        ex = entry(Array(map(String, sys.argv[1:])))
    else:
        raise SamariumSyntaxError("entry function should take 0 or 1 arguments")
    if not is_class:
        sys.exit(ex.value)
