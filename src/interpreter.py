import objects
import sys
from transpiler import CodeHandler
from core import run, readfile

PUBLIC = CodeHandler(globals())
IMPORTED = CodeHandler(globals())


def main():
    run(readfile(sys.argv[1]), ch=PUBLIC, imported=IMPORTED)


if __name__ == "__main__":
    main()
