from __future__ import annotations

from collections.abc import Callable
from enum import Enum as PyEnum
from functools import wraps
from io import BufferedIOBase, IOBase
from typing import Any
from typing import Iterable as PyIterable
from typing import TypeVar

from samarium.classes import (
    NULL,
    Array,
    Attrs,
    File,
    Integer,
    Iterator,
    Null,
    Slice,
    String,
    Table,
)
from samarium.classes.base import Enum, Int, Zip


class SliceRange:
    def __init__(self, slice_: Slice) -> None:
        self._slice = slice_

    @property
    def slice(self) -> slice:
        return self._slice.val

    @property
    def range(self) -> range:
        return self._slice.range


F = TypeVar("F", bound=Callable)


def export(f: F) -> F:
    """Marks an object to be exported to Samarium"""
    setattr(f, f"__export_{f}", True)
    return f


def to_python(obj: Attrs) -> object:
    if isinstance(obj, (String, Integer, Zip, File)):
        return obj.val
    elif isinstance(obj, Null):
        return None
    elif isinstance(obj, Array):
        return [to_python(i) for i in obj.val]
    elif isinstance(obj, Table):
        return {to_python(k): to_python(v) for k, v in obj.val.items()}
    elif isinstance(obj, Slice):
        return SliceRange(obj)
    elif isinstance(obj, Zip):
        return obj.val
    elif isinstance(obj, Enum):
        o = {k.removeprefix("sm_"): to_python(v) for k, v in obj.members.items()}
        return PyEnum(obj.name, *o)
    elif isinstance(obj, Iterator):
        return (to_python(i) for i in obj)


def to_samarium(obj: object) -> Attrs:
    if isinstance(obj, (int, bool, float)):
        return Int(obj)
    elif isinstance(obj, str):
        return String(obj)
    elif obj is None:
        return NULL
    elif isinstance(obj, (list, tuple, set)):
        return Array([to_samarium(i) for i in obj])
    elif isinstance(obj, dict):
        return Table({to_samarium(k): to_samarium(v) for k, v in obj.items()})
    elif isinstance(obj, (range, slice)):
        return Slice(
            to_samarium(obj.start), to_samarium(obj.stop), to_samarium(obj.step)
        )
    elif isinstance(obj, SliceRange):
        return obj._slice
    elif isinstance(obj, IOBase):
        return File(obj, obj.mode, obj.name, isinstance(obj, BufferedIOBase))  # type: ignore
    elif isinstance(obj, zip):
        return Zip(*obj)
    elif isinstance(obj, PyEnum):
        o = {k: to_samarium(v) for k, v in obj.__members__.items()}
        return Enum("PyEnum", *o)

    elif isinstance(obj, PyIterable):
        return Iterator(obj)
    raise TypeError(f"Conversion for type {type(obj)} not found")


def sm_function(func):
    """Wraps a Python function to be used in Samarium"""

    @wraps(func)
    def wrapper(*_args):
        args = map(to_python, _args)
        return to_samarium(func(*args))

    return wrapper


def py_function(func):
    """Converts a Samarium function to be used in Python"""

    @wraps(func)
    def wrapper(*_args):
        args = map(to_samarium, _args)
        return to_python(func(*args))

    return wrapper


class SmProxy(Attrs):
    """Allows the use of a Python object via Samarium"""

    def __init__(self, v: Any) -> None:
        self.v = v

    def __call__(self, *args, **kwargs):
        return sm_function(self.v)(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:  # type: ignore
        if name.startswith("sm_"):
            attr = getattr(self.v, name.removeprefix("sm_"))

            if callable(attr):
                return SmProxy(attr)  # type: ignore
            return to_samarium(attr)
        return self.__getattribute__(name)


class PyProxy:
    """Allows the use of a Samarium object via Python"""

    def __init__(self, v: Any) -> None:
        self.v = v

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return py_function(self.v)(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("__"):
            return getattr(self, name)
        attr = getattr(self.v, f"sm_{name}")
        if callable(attr):
            return PyProxy(attr)
        return to_python(attr)
