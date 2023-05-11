import sys

if sys.platform not in ("win32", "cygwin"):
    # used by input() to provide elaborate line editing & history features
    import readline

from crossandra import CrossandraError

from samarium.core import run
from samarium.exceptions import SamariumSyntaxError, handle_exception
from samarium.runtime import Runtime
from samarium.tokenizer import tokenize
from samarium.transpiler import Registry, match_brackets
from samarium.utils import __version__

IN = "--> "
INDENT = "  > "


def read_statement() -> str:
    statement = ""
    prompt = IN
    while True:
        statement += input(prompt)
        if statement:
            statement += ";"
            try:
                error, stack = match_brackets(tokenize(statement, repl=True))
            except CrossandraError as e:
                if '"' in str(e):
                    error, stack = 1, []
                else:
                    handle_exception(SamariumSyntaxError(str(e)))
                    raise RuntimeError from None

            if not error:
                return statement
            if error == -1:
                handle_exception(
                    SamariumSyntaxError(
                        f"missing opening bracket for {stack[-1].value}"
                    )
                )
                raise RuntimeError from None

            prompt = INDENT
            statement = statement[:-1] + "\n"


def run_repl(*, debug: bool) -> None:
    print(f"Samarium {__version__}" + " [DEBUG]" * debug)
    main = Registry(globals())
    Runtime.repl = True
    while True:
        try:
            run(
                read_statement(),
                main,
                "",
                debug=debug,
                load_template=False,
                repl=True,
            )
            main.output = ""
        except RuntimeError:
            pass
        except KeyboardInterrupt:
            print()
        except EOFError:
            break
