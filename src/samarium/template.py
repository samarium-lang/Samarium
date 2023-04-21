import sys

__file__ = "{{ SOURCE }}"
{{ CODE }}
if __name__ == "samarium":
    try:
        entry
    except NameError:
        sys.exit()
    argc = entry.special()
    is_class = isinstance(entry, type)
    if is_class:
        argc -= 1
    if not argc.val:
        ex = entry()
    elif argc.val == 1:
        ex = entry(Array(map(String, sys.argv[1:])))
    else:
        raise exceptions.SamariumSyntaxError(
            "entry function should take 0 or 1 arguments"
        )
    if not is_class:
        sys.exit(ex.val)
