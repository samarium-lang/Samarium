import sys

__file__ = "{{ SOURCE }}"
{{ CODE }}
if __name__ == "samarium":
    try:
        entry
    except NameError:
        sys.exit()
    argc = param_count(entry)
    is_class = isinstance(entry, type)
    if is_class:
        argc -= 1
    if not argc:
        ex = entry()
    elif argc == 1:
        ex = entry(Array(map(String, sys.argv[1:])))
    else:
        raise SamariumSyntaxError("entry function should take 0 or 1 arguments")
    if not is_class:
        sys.exit(ex.val)
