from dahlia import dahlia, dprint

from .core import run
from .tokenizer import tokenize
from .transpiler import Registry
from .utils import match_brackets, __version__


IN = dahlia("&3==> ")
INDENT = dahlia("&3  > ")


def read_statement() -> str:
    statement = ""
    prompt = IN
    while True:
        statement += input(prompt)
        if statement:
            statement += " ;"
            error, _ = match_brackets(tokenize(statement))
            if not error:
                return statement
            prompt = INDENT
            statement = statement[:-1]


def run_shell(debug: bool):
    dprint(f"&3Samarium {__version__}")
    MAIN = Registry(globals())
    while True:
        try:
            run(read_statement(), MAIN, debug, load_template=False, quit_on_error=False)
            MAIN.output *= 0
        except KeyboardInterrupt:
            print()
        except EOFError:
            break
