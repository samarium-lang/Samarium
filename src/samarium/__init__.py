import sys
from contextlib import suppress
from .transpiler import CodeHandler
from .core import run, readfile

MAIN = CodeHandler(globals())

OPTIONS = ["-v", "--version", "-c", "--command", "-h", "--help"]

HELP = """samarium [option] [-c cmd | file]
options and arguments:
-c, --command cmd : reads program from string
-h, --help        : shows this
-v, --version     : prints Samarium version
file              : reads program from script file"""


def main(debug: bool = False):

    try:
        arg = sys.argv[1]
    except IndexError:
        arg = "-v"

    if arg in OPTIONS:
        q = 0
        if arg in OPTIONS[:2]:
            print("Samarium 0.2.0-alpha.1")
        elif arg in OPTIONS[2:4]:
            q = run(f"=> argv * {{{sys.argv[2]}!;}}", MAIN, debug)
        elif arg in OPTIONS[4:]:
            print(HELP)
        sys.exit(q)

    try:
        file = readfile(arg)
    except IOError:
        print(f"file not found: {arg}")
    else:
        with suppress(Exception, KeyboardInterrupt):
            file = "\n".join(file.splitlines()[file.startswith("#!"):])
            run(file, MAIN, debug)


def main_debug():
    main(debug=True)
