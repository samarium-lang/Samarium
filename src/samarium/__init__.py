import sys
from contextlib import suppress
from .transpiler import CodeHandler
from .core import run, readfile

MAIN = CodeHandler(globals())


def main():
    if sys.argv[1] == "-v":
        sys.exit(print("Samarium 0.1.0"))
    with suppress(Exception, KeyboardInterrupt):
        run(readfile(sys.argv[1]), MAIN)
