from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from inspect import signature
from re import compile
from time import sleep as _sleep
from time import time_ns
from types import FunctionType, GeneratorType
from typing import Any, Callable
from typing import Iterator as Iter
from typing import TypeVar

from .classes import (
    MISSING,
    NULL,
    Array,
    Attrs,
    Int,
    Integer,
    Iterator,
    Null,
    Slice,
    String,
    Type,
    to_string,
)
from .exceptions import (
    SamariumError,
    SamariumIOError,
    SamariumSyntaxError,
    SamariumTypeError,
)
from .utils import get_name

MISSING_ARGS_PATTERN = compile(
    r"\w+\(\) takes exactly one argument \(0 given\)"
    r"|\w+\(\) missing (\d+) required positional argument"
)

NULL_STRING = String()

T = TypeVar("T")

TOO_MANY_ARGS_PATTERN = compile(
    r"\w+\(\) takes (\d+) positional arguments? but (\d+) (?:was|were) given"
)


def check_type(obj: Any) -> None:
    if isinstance(obj, property):
        raise SamariumTypeError("cannot use a special method on a type")
    if isinstance(obj, (tuple, GeneratorType)):
        raise SamariumSyntaxError("invalid syntax")


def correct_type(obj: T) -> T | Integer | Iterator | Null:
    if obj is None:
        return NULL
    elif isinstance(obj, bool):
        return Int(obj)
    elif isinstance(obj, GeneratorType):
        return Iterator(obj)
    else:
        check_type(obj)
    return obj


def dtnow() -> Array:
    utcnow = datetime.utcnow()
    now = datetime.now().timetuple()
    utcnow_tt = utcnow.timetuple()
    tz = now[3] - utcnow_tt[3], now[4] - utcnow_tt[4]
    utcnow_tpl = utcnow_tt[:-3] + (utcnow.microsecond // 1000,) + tz
    return Array(map(Int, utcnow_tpl))


def function(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any) -> Any:
        for arg in args:
            check_type(arg)
        with modify(func, list(args), argc) as (f, checked_args):
            try:
                result = correct_type(f(*checked_args))
            except TypeError as e:
                errmsg = str(e)
                if "positional argument: 'self'" in errmsg:
                    raise SamariumTypeError("missing instance") from None
                missing_args = MISSING_ARGS_PATTERN.search(errmsg)
                if missing_args:
                    given = argc - (int(missing_args.group(1)) or 1)
                    raise SamariumTypeError(
                        f"not enough arguments ({given}/{argc})"
                    ) from None
                too_many_args = TOO_MANY_ARGS_PATTERN.search(errmsg)
                if too_many_args:
                    raise SamariumTypeError(
                        f"too many arguments ({too_many_args.group(2)}/{argc})"
                    ) from None
                raise e
        return result

    argc = len(signature(func).parameters)

    wrapper.__str__ = lambda: get_name(func)
    wrapper.special = lambda: Int(argc)
    wrapper.argc = argc
    wrapper.parent = lambda: Type(FunctionType)
    wrapper.type = lambda: Type(FunctionType)
    wrapper.hash = lambda: Int(hash(func))

    return wrapper


@contextmanager
def modify(
    func: Callable[..., Any], args: list[Any], argc: int
) -> Iter[tuple[Callable[..., Any], list[Any]]]:
    flag = func.__code__.co_flags
    if flag & 4 == 0:
        yield func, args
        return
    x = argc - 1
    args = [*args[:x], Array(args[x:])]
    func.__code__ = func.__code__.replace(co_flags=flag - 4, co_argcount=argc)
    if not argc:
        args = []
    yield func, args
    func.__code__ = func.__code__.replace(co_flags=flag, co_argcount=argc - 1)


def mkslice(start: Any = None, stop: Any = MISSING, step: Any = None) -> Any:
    if stop is MISSING:
        if start is not None:
            return start
        return Slice(NULL)
    start = NULL if start is None else start
    stop = NULL if stop is None else stop
    step = NULL if step is None else step
    return Slice(start, stop, step)


def print_safe(*args: Attrs | Callable[..., Any] | bool | None) -> Attrs:
    typechecked_args = list(map(correct_type, args))
    return_args = typechecked_args.copy()
    strs = list(map(to_string, typechecked_args))
    types = list(map(type, typechecked_args))
    if tuple in types:
        raise SamariumSyntaxError("missing brackets")
    if GeneratorType in types:
        raise SamariumSyntaxError("invalid comprehension")
    print(*strs)
    if len(return_args) > 1:
        return Array(return_args)
    elif not return_args or types[0] is Null:
        return NULL
    return return_args[0]


def readline(prompt: String = NULL_STRING) -> String:
    try:
        return String(input(prompt.val))
    except KeyboardInterrupt:
        msg = "^C"
    except EOFError:
        msg = "^D"
    raise SamariumIOError(msg)


def sleep(*args: Integer) -> None:
    if not args:
        raise SamariumTypeError("no argument provided for ,.,")
    if len(args) > 1:
        raise SamariumTypeError(",., only takes one argument")
    if not isinstance((time := args[0]), Integer):
        raise SamariumTypeError(",., only accepts integers")
    _sleep(time.val / 1000)


def t(obj: T | None = None) -> T | None:
    return obj


def throw(message: String = NULL_STRING) -> None:
    raise SamariumError(message.val)


def timestamp() -> Integer:
    return Int(time_ns() // 1_000_000)
