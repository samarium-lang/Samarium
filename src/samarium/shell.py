from termcolor import colored

from .core import run
from .tokenizer import tokenize
from .transpiler import CodeHandler
from .utils import match_brackets, __version__


def read_statement():
    IN = colored("::> ", "magenta")
    INDENT = colored("  : ", "magenta")
    statement = ""
    prompt = IN
    while True:
        statement += input(prompt)
        if statement:
            statement += ";"
            error, _ = match_brackets(tokenize(statement))
            if not error:
                return statement
            prompt = INDENT
            statement = statement[:-1]


def run_shell(debug: bool):
    print(colored(f"Samarium {__version__}", "magenta"))
    MAIN = CodeHandler(globals())
    while True:
        run(read_statement(), MAIN, debug, load_template=False)
        MAIN.code *= 0
