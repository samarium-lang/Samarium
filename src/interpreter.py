import sys
from parser import CodeHandler
from core import run, readfile

PUBLIC = CodeHandler(globals())
imported = CodeHandler(globals())


def main():
    run(readfile(sys.argv[1]), ch=PUBLIC, imported=imported)


if __name__ == "__main__":
    main()
