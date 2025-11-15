import sys
from contextlib import nullcontext, suppress
from pathlib import Path

from samarium.core import run
from samarium.exceptions import DAHLIA
from samarium.repl import REPL, Command
from samarium.transpiler import Registry
from samarium.utils import __version__

OPTIONS = ("-v", "--version", "-c", "--command", "-h", "--help")

HELP = """samarium &7[option] [-c cmd | file]&R
options and arguments:\n""" + "\n".join(
    map(
        str,
        (
            Command(
                "-c",
                "--command",
                arg="<cmd>",
                sep=", ",
                msg="reads program from string",
            ),
            Command("-h", "--help", sep=", ", msg="shows this message"),
            Command("-v", "--version", sep=", ", msg="prints Samarium version"),
            Command(arg="file", sep=", ", msg=" reads program from script file"),
        ),
    )
)


def main(*, debug: bool = False) -> None:
    reg = Registry(globals())

    if len(sys.argv) == 1:
        return REPL(debug=debug).run()

    if (arg := sys.argv[1]) in OPTIONS:
        if arg in OPTIONS[:2]:
            print(f"Samarium {__version__}")
        elif arg in OPTIONS[2:4]:
            if len(sys.argv) > 2:
                run(sys.argv[2] + " !", reg, arg, debug=debug)
            DAHLIA.print("&4missing code to execute", file=sys.stderr)
        elif arg in OPTIONS[4:]:
            DAHLIA.print(HELP)
        sys.exit()

    try:
        file = Path(arg).read_text()
    except OSError:
        DAHLIA.print(f"&4file not found: {arg}", file=sys.stderr)
    else:
        with nullcontext() if debug else suppress(Exception, KeyboardInterrupt):
            file = "\n".join(file.splitlines()[file.startswith("#!") :])
            run(file, reg, arg, debug=debug)


def main_debug() -> None:
    main(debug=True)
