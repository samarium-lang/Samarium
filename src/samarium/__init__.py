import sys
from contextlib import suppress
from .transpiler import CodeHandler
from .core import run, readfile

MAIN = CodeHandler(globals())


def main():
    with suppress(Exception, KeyboardInterrupt):
        run(readfile(sys.argv[1]), MAIN)
