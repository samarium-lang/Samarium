import sys

from contextlib import suppress

from .core import run, readfile
from .shell import run_shell
from .transpiler import CodeHandler
from .utils import __version__

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
        return run_shell(debug)

    if arg in OPTIONS:
        q = 0
        if arg in OPTIONS[:2]:
            print(f"Samarium {__version__}")
        elif arg in OPTIONS[2:4]:
            q = run(f"=> argv * {{\n\t{sys.argv[2]}!;\n}}", MAIN, debug)
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
