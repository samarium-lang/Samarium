from __future__ import annotations

import os
import sys
from collections import Counter
from collections.abc import Callable
from contextlib import contextmanager, suppress
from re import sub
from string import digits, hexdigits, octdigits
from typing import Any, Generic, Iterator, TypeVar, cast

from .exceptions import NotDefinedError, SamariumTypeError, SamariumValueError
from .tokenizer import Tokenlike
from .tokens import CLOSE_TOKENS, OPEN_TOKENS, Token

__version__ = "0.4.0-alpha"

T = TypeVar("T")

OPEN_TO_CLOSE = {
    Token.BRACKET_OPEN: Token.BRACKET_CLOSE,
    Token.BRACE_OPEN: Token.BRACE_CLOSE,
    Token.PAREN_OPEN: Token.PAREN_CLOSE,
    Token.TABLE_OPEN: Token.TABLE_CLOSE,
    Token.SLICE_OPEN: Token.SLICE_CLOSE,
}


KT = TypeVar("KT")
VT = TypeVar("VT")


class ClassProperty:
    def __init__(self, func: Callable[..., Any]) -> None:
        self.func = func

    def __get__(self, obj: Any, owner: Any | None = None) -> Any:
        if obj is None:
            obj = owner
        return self.func(obj)


class LFUCache(Generic[KT, VT]):
    def __init__(self, maxsize: int = 1024) -> None:
        self._cache: dict[KT, VT] = {}
        self._maxsize = maxsize
        self._heatmap: Counter[KT] = Counter()

    def __contains__(self, item: KT) -> bool:
        return item in self._cache

    def __getitem__(self, item: KT) -> VT:
        self._heatmap[item] -= 1
        return self._cache[item]

    def __setitem__(self, item: KT, value: VT) -> None:
        if len(self._cache) == self._maxsize:
            del self[self._heatmap.most_common(1)[0][0]]
        self._cache[item] = value
        self._heatmap[item] = 0

    def __delitem__(self, item: KT) -> None:
        del self._cache[item]
        del self._heatmap[item]


class Singleton:
    _instances: dict[type[Singleton], Singleton] = {}

    def __new__(cls, *args: Any, **kwargs: Any):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instances[cls]


def match_brackets(tokens_: list[Tokenlike]) -> tuple[int, list[Token]]:
    stack: list[Token] = []
    token = Token.END
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
            return -1, [Token.END, token]
    if stack:
        return 1, [token]
    return 0, []


def run_with_backup(main: Callable[..., T], backup: Callable[..., T], *args: Any) -> T:
    with suppress(NotDefinedError):
        return main(*args)
    return backup(*args)


@contextmanager
def silence_stdout() -> Iterator[None]:
    stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")
    yield
    sys.stdout = stdout


def sysexit(*args: Any):
    if len(args) > 1:
        raise SamariumTypeError("=>! only takes one argument")
    code = args[0].val if args else 0
    if not isinstance(code, int):
        raise SamariumTypeError("=>! only accepts integers")
    raise SystemExit(code)


def parse_integer(string: str) -> int:
    string = string.strip()
    orig = string
    neg = len(string)
    b = "d"
    if ":" in string:
        b, string = string.split(":", 1)
        if b not in "box":
            raise SamariumValueError(f"{b} is not a valid base")
    base = {"b": 2, "o": 8, "x": 16, "d": 10}[b]
    string = string.lstrip("-")
    digitset = {2: "01", 8: octdigits, 10: digits, 16: hexdigits}[base]
    neg -= len(string)
    neg %= 2
    if string and all(i in digitset for i in string.lower()):
        return int("-" * neg + string, base)
    no_prefix = orig[2:] if orig[1] == ":" else orig
    raise SamariumValueError(
        f'invalid string for Integer with base {base}: "{no_prefix}"'
    )


def smformat(string: str, fields: str | list[Any] | dict[Any, Any]) -> str:
    if isinstance(fields, str):
        fields = [fields]
    it = enumerate(fields)
    if isinstance(fields, dict):
        it = fields.items()
    for k, v in it:
        string = sub(rf"(?<!\$)\${k}", str(v), string)
    return string.replace("$$", "$")


def get_name(obj: Callable[..., Any] | type) -> str:
    return obj.__name__.removeprefix("sm_")


def get_type_name(obj: Any) -> str:
    return type(obj).__name__.removeprefix("sm_")


def guard(operator: str) -> Callable[..., Any]:
    def decorator(function: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(self: Any, other: Any) -> Any:
            Ts = type(self)
            To = type(other)
            if isinstance(other, Ts):
                return function(self, other)
            raise NotDefinedError(f"{Ts.__name__} {operator} {To.__name__}")

        return wrapper

    return decorator
