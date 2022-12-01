from __future__ import annotations

from enum import Enum as PyEnum
from functools import wraps
from io import BufferedIOBase, IOBase
from types import FunctionType
from typing import Iterable as PyIterable

from samarium.classes import (
    NULL,
    Array,
    Attrs,
    Enum,
    File,
    Int,
    Integer,
    Iterator,
    Mode,
    Null,
    Slice,
    String,
    Table,
    Zip,
)


class SliceRange:
    def __init__(self, slice_: Slice) -> None:
        self._slice = slice_

    @property
    def slice(self) -> slice:
        return self._slice.val

    @property
    def range(self) -> range:
        return self._slice.range


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
    elif isinstance(obj, Enum):
        o = {k.removeprefix("sm_"): to_python(v) for k, v in obj.members.items()}
        return PyEnum(obj.name, o)
    elif isinstance(obj, Iterator):
        return map(to_python, obj)
    raise TypeError(f"Conversion for type {type(obj).__name__!r} not found")


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
            to_samarium(None if obj.start == 0 else obj.start),
            to_samarium(obj.stop),
            to_samarium(None if obj.step == 1 else obj.step),
        )
    elif isinstance(obj, SliceRange):
        return obj._slice
    elif isinstance(obj, IOBase):
        return File(obj, Mode(obj.mode).name, obj.name, binary=isinstance(obj, BufferedIOBase))  # type: ignore
    elif isinstance(obj, zip):
        return Zip(*obj)
    elif isinstance(obj, type) and issubclass(obj, PyEnum):
        o = {f"sm_{k}": to_samarium(v) for k, v in obj.__members__.items()}
        return Enum(f"sm_{obj.__name__}", **o)
    elif isinstance(obj, PyEnum):
        return to_samarium(obj.value)
    elif isinstance(obj, PyIterable):
        return Iterator(obj)
    raise TypeError(f"Conversion for type {type(obj).__name__!r} not found")


def export(func):
    """Wraps a Python function to be used in Samarium"""

    @wraps(func)
    def wrapper(*_args):
        args = map(to_python, _args)
        return to_samarium(func(*args))

    if not isinstance(func, FunctionType):
        raise TypeError(
            f"cannot export a non-function type {type(func).__name__!r}"
        )
    setattr(wrapper, f"__export_{wrapper}", True)

    return wrapper
