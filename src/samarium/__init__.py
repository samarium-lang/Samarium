import sys
from contextlib import suppress
from .transpiler import CodeHandler
from .core import run, readfile

MAIN = CodeHandler(globals())


def main(debug: bool = False):
    if sys.argv[1] == "-v":
        print("Samarium 0.1.0")
    elif sys.argv[1] == "-c":
        sys.exit(run(f"=> * {{{sys.argv[2]}!;}}", MAIN, debug))
    else:
        try:
            readfile(sys.argv[1])
        except IOError:
            print(f"file not found: {sys.argv[1]}")
        with suppress(Exception, KeyboardInterrupt):
            run(readfile(sys.argv[1]), MAIN, debug)


def main_debug():
    main(debug=True)
