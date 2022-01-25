import sys
from contextlib import suppress
from transpiler import CodeHandler
from core import run, readfile

MAIN = CodeHandler(globals())


def main():
    run(readfile(sys.argv[1]), MAIN)


if __name__ == "__main__":
    with suppress(BaseException):
        main()
