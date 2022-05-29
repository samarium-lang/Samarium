import os
import sys

from contextlib import contextmanager, suppress
from string import digits, hexdigits, octdigits
from typing import Any, Callable, TypeVar

from .exceptions import NotDefinedError, SamariumTypeError, SamariumValueError
from .tokenizer import Tokenlike
from .tokens import Token, OPEN_TOKENS, CLOSE_TOKENS

__version__ = "0.2.0-beta.1"

T = TypeVar("T")

OPEN_TO_CLOSE = {
    Token.BRACKET_OPEN: Token.BRACKET_CLOSE,
    Token.BRACE_OPEN: Token.BRACE_CLOSE,
    Token.PAREN_OPEN: Token.PAREN_CLOSE,
    Token.TABLE_OPEN: Token.TABLE_CLOSE,
    Token.SLICE_OPEN: Token.SLICE_CLOSE,
}


def match_brackets(tokens: list[Tokenlike]) -> tuple[int, Tokenlike]:
    stack = []
    for token in tokens:
        if token in OPEN_TOKENS:
            stack += [token]
        elif token in CLOSE_TOKENS:
            if OPEN_TO_CLOSE[stack[-1]] == token:
                stack.pop(-1)
            else:
                return 1, token
    if stack:
        return -1, stack[-1]
    return 0, 0


def readfile(path: str) -> str:
    with open(path) as f:
        return f.read()


def run_with_backup(main: Callable[..., T], backup: Callable[..., T], *args) -> T:
    with suppress(NotDefinedError):
        return main(*args)
    return backup(*args)


@contextmanager
def silence_stdout():
    stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")
    yield
    sys.stdout = stdout


def sysexit(*args: Any):
    if len(args) > 1:
        raise SamariumTypeError("=>! only takes one argument")
    code = args[0].value if args else 0
    if not isinstance(code, int):
        raise SamariumTypeError("=>! only accepts integers")
    os._exit(code)


def parse_integer(string: str) -> int:
    orig = string
    neg = len(string)
    b = "d"
    if ":" in string:
        b, string = string.split(":")
        if b not in "box":
            raise SamariumValueError(f"{b} is not a valid base")
    base = {
        "b": 2,
        "o": 8,
        "x": 16,
        "d": 10,
    }[b]
    string = string.lstrip("-")
    digitset = {
        2: "01",
        8: octdigits,
        10: digits,
        16: hexdigits,
    }[base]
    neg -= len(string)
    neg %= 2
    if all(i in digitset for i in string.lower()):
        return int("-" * neg + string, base)
    raise SamariumValueError(f'invalid string for Integer with base {base}: "{orig}"')


def get_function_name(function: Callable) -> str:
    return function.__name__.strip("_")
