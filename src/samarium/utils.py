from __future__ import annotations

from re import sub
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar

from samarium.exceptions import SamariumTypeError, SamariumValueError

if TYPE_CHECKING:
    from collections.abc import Callable

__version__ = "0.6.0"

T = TypeVar("T")


KT = TypeVar("KT")
VT = TypeVar("VT")


class ClassProperty(Generic[T]):
    def __init__(self, func: Callable[..., T]) -> None:
        self.func = func

    def __get__(self, obj: object, owner: object = None) -> T:
        if obj is None:
            obj = owner
        return self.func(obj)


class Singleton:
    _instances: ClassVar[dict[type[Singleton], Singleton]] = {}

    def __new__(cls, *args: Any, **kwargs: Any) -> Singleton:
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls, *args, **kwargs)
        return cls._instances[cls]


def sysexit(*args: Any) -> None:
    if len(args) > 1:
        msg = "=>! only takes one argument"
        raise SamariumTypeError(msg)
    code = args[0].val if args else 0
    if not isinstance(code, (int, str)):
        msg = "=>! only accepts integers and strings"
        raise SamariumTypeError(msg)
    raise SystemExit(code)


def convert_float(string: str, *, base: int, sep: str = ".") -> int | float:
    exp_sep = "p" if base == 16 else "e"
    if not (sep in string or exp_sep in string):
        return int(string, base)
    float_part, _, exp_part = string.partition(exp_sep)
    int_, _, dec = float_part.partition(sep)
    out = int(int_ or "0", base) + sum(
        int(v, base) * base**~i for i, v in enumerate(dec)
    )
    if exp_part:
        try:
            exponent = int(exp_part, 10 if base == 16 else base)
        except ValueError:
            msg = f"invalid exponent: {exp_part}"
            raise SamariumValueError(msg) from None
        out *= (2 if base == 16 else base) ** exponent
    return out


def parse_number(string: str) -> tuple[int | float, bool]:
    string = string.strip()
    orig = string
    neg = len(string)
    b = "d"
    if ":" in string:
        b, _, string = string.partition(":")
        if b not in "box":
            msg = f"{b} is not a valid base"
            raise SamariumValueError(msg)
    base = {"b": 2, "o": 8, "x": 16, "d": 10}[b]
    string = string.lstrip("-")
    neg = -2 * ((neg - len(string)) % 2) + 1

    try:
        num = neg * convert_float(string, base=base)
    except ValueError:
        no_prefix = orig[2:] if orig[1] == ":" else orig
        msg = f'invalid string for Number with base {base}: "{no_prefix}"'
        raise SamariumValueError(
            msg
        ) from None
    else:
        return num, isinstance(num, int) or num.is_integer()


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
