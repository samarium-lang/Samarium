from __future__ import annotations

from collections.abc import Callable
from typing import Any, Generic, TypeVar
from functools import wraps
from samarium.classes import (
    NULL,
    Array,
    Integer,
    Null,
    String,
    Table,
)
from samarium.classes.base import Attrs

F = TypeVar("F", bound=Callable)


class PythonExport(Generic[F]):
    def __init__(self, o: F) -> None:
        self.o = o


def export(func: F) -> PythonExport[F]:
    """Marks an object to be exported to Samarium"""
    return PythonExport(func)


def to_python(obj: Attrs) -> object:
    if isinstance(obj, (String, Integer)):
        return obj.val
    elif isinstance(obj, Null):
        return None
    elif isinstance(obj, Array):
        return [to_python(i) for i in obj.val]
    elif isinstance(obj, Table):
        return {to_python(k): to_python(v) for k, v in obj.val.items()}


def to_samarium(obj: object) -> Attrs | type[Attrs]:
    if isinstance(obj, (int, bool)):
        return Integer(obj)
    elif isinstance(obj, str):
        return String(obj)
    elif obj is None:
        return NULL
    elif isinstance(obj, (list, tuple, set)):
        return Array([to_samarium(i) for i in obj])
    elif isinstance(obj, dict):
        return Table({to_samarium(k): to_samarium(v) for k, v in obj.items()})


def function(func):
    """Wraps a Python function to be used in Samarium"""
    @wraps(func)
    def wrapper(*_args):
        args = map(to_python, _args)
        return to_samarium(func(*args))

    return wrapper


class SmProxy(Attrs):

    def __init__(self, v: Any) -> None:
        self.v = v

    def __getattr__(self, name: str) -> Any:  # type: ignore
        if name.startswith("sm_"):
            attr = getattr(self.v, name.removeprefix("sm_"))

            if callable(attr):
                return function(attr)  # type: ignore
            return to_samarium(attr)
        return self.__getattribute__(name)
