import sys
from contextlib import suppress
from .transpiler import CodeHandler
from .core import run, readfile

MAIN = CodeHandler(globals())


def main(debug: bool = False):
    if sys.argv[1] == "-v":
        sys.exit(print("Samarium 0.1.0"))
    elif sys.argv[1] == "-c":
        sys.exit(run(f"=> argv * {{{sys.argv[2]}!;}}", MAIN, debug))
    try:
        file = readfile(sys.argv[1])
    except IOError:
        print(f"file not found: {sys.argv[1]}")
    else:
        with suppress(Exception, KeyboardInterrupt):
            run(file, MAIN, debug)


def main_debug():
    main(debug=True)
