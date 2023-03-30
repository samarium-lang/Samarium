import sys
from contextlib import suppress
from pathlib import Path

from .core import run
from .exceptions import DAHLIA
from .shell import run_shell
from .transpiler import Registry
from .utils import __version__

OPTIONS = ("-v", "--version", "-c", "--command", "-h", "--help")

HELP = """samarium [option] [-c cmd | file]
options and arguments:
-c, --command cmd : reads program from string
-h, --help        : shows this
-v, --version     : prints Samarium version
file              : reads program from script file"""


def main(*, debug: bool = False) -> None:

    reg = Registry(globals())

    if len(sys.argv) == 1:
        return run_shell(debug=debug)

    if (arg := sys.argv[1]) in OPTIONS:
        if arg in OPTIONS[:2]:
            print(f"Samarium {__version__}")
        elif arg in OPTIONS[2:4]:
            if len(sys.argv) > 2:
                run(sys.argv[2] + " !;", reg, arg, debug=debug)
            DAHLIA.print("&4missing code to execute", file=sys.stderr)
        elif arg in OPTIONS[4:]:
            print(HELP)
        sys.exit()

    try:
        file = Path(arg).read_text()
    except IOError:
        DAHLIA.print(f"&4file not found: {arg}", file=sys.stderr)
    else:
        with suppress(Exception, KeyboardInterrupt):
            file = "\n".join(file.splitlines()[file.startswith("#!") :])
            run(file, reg, arg, debug=debug)


def main_debug() -> None:
    main(debug=True)
