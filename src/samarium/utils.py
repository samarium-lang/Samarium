import os
import sys

from contextlib import contextmanager, suppress
from string import digits, hexdigits, octdigits
from typing import Any, Callable, TypeVar, cast

from .exceptions import NotDefinedError, SamariumTypeError, SamariumValueError
from .tokenizer import Tokenlike
from .tokens import Token, OPEN_TOKENS, CLOSE_TOKENS

__version__ = "0.2.2"

T = TypeVar("T")

OPEN_TO_CLOSE = {
    Token.BRACKET_OPEN: Token.BRACKET_CLOSE,
    Token.BRACE_OPEN: Token.BRACE_CLOSE,
    Token.PAREN_OPEN: Token.PAREN_CLOSE,
    Token.TABLE_OPEN: Token.TABLE_CLOSE,
    Token.SLICE_OPEN: Token.SLICE_CLOSE,
}


def match_brackets(tokens_: list[Tokenlike]) -> tuple[int, list[Token]]:
    stack = []
    token = Token.NULL
    tokens: list[Token] = [
        cast(Token, t) for t in tokens_ if t in OPEN_TOKENS + CLOSE_TOKENS
    ]
    for token in tokens:
        if token in OPEN_TOKENS:
            stack.append(token)
        elif stack:
            if OPEN_TO_CLOSE[stack[-1]] == token:
                stack.pop()
            else:
                return -1, [stack[-1], token]
        else:
            return -1, [Token.NULL, token]
    if stack:
        return 1, [token]
    return 0, []


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
    base = {"b": 2, "o": 8, "x": 16, "d": 10}[b]
    string = string.lstrip("-")
    digitset = {2: "01", 8: octdigits, 10: digits, 16: hexdigits}[base]
    neg -= len(string)
    neg %= 2
    if all(i in digitset for i in string.lower()):
        return int("-" * neg + string, base)
    raise SamariumValueError(f'invalid string for Integer with base {base}: "{orig}"')


def get_callable_name(function: Callable) -> str:
    return function.__name__.strip("_")
