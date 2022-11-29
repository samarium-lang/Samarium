import readline  # type: ignore

from .core import run
from .tokenizer import tokenize
from .transpiler import Registry
from .utils import __version__, match_brackets

# ^ used by input() to provide elaborate line editing and history features


IN = "--> "
INDENT = "  > "


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


def run_shell(debug: bool) -> None:
    print(f"Samarium {__version__}" + " [DEBUG]" * debug)
    main = Registry(globals())
    while True:
        try:
            run(read_statement(), main, debug, load_template=False)
            main.output = ""
        except KeyboardInterrupt:
            print()
        except EOFError:
            break
