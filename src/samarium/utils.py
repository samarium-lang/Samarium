from __future__ import annotations

from collections.abc import Callable
from re import sub
from typing import Any, TypeVar

from .exceptions import SamariumTypeError, SamariumValueError

__version__ = "0.5.0"

T = TypeVar("T")


KT = TypeVar("KT")
VT = TypeVar("VT")


class ClassProperty:
    def __init__(self, func: Callable[..., Any]) -> None:
        self.func = func

    def __get__(self, obj: Any, owner: Any | None = None) -> Any:
        if obj is None:
            obj = owner
        return self.func(obj)


class Singleton:
    _instances: dict[type[Singleton], Singleton] = {}

    def __new__(cls, *args: Any, **kwargs: Any):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls, *args, **kwargs)
        return cls._instances[cls]


def sysexit(*args: Any) -> None:
    if len(args) > 1:
        raise SamariumTypeError("=>! only takes one argument")
    code = args[0].val if args else 0
    if not isinstance(code, int):
        raise SamariumTypeError("=>! only accepts integers")
    raise SystemExit(code)


def convert_float(string: str, *, base: int, sep: str = ".") -> int | float:
    int_, _, dec = string.partition(sep)
    return int(int_ or "0", base) + sum(
        int(v, base) * 2**~i for i, v in enumerate(dec)
    )


def parse_number(string: str) -> tuple[int | float, bool]:
    string = string.strip()
    orig = string
    neg = len(string)
    b = "d"
    if ":" in string:
        b, _, string = string.partition(":")
        if b not in "box":
            raise SamariumValueError(f"{b} is not a valid base")
    base = {"b": 2, "o": 8, "x": 16, "d": 10}[b]
    string = string.lstrip("-")
    neg = -2 * ((neg - len(string)) % 2) + 1

    try:
        num = neg * convert_float(string, base=base)
        return num, isinstance(num, int)
    except ValueError:
        no_prefix = orig[2:] if orig[1] == ":" else orig
        raise SamariumValueError(
            f'invalid string for Number with base {base}: "{no_prefix}"'
        ) from None


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
