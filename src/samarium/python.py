from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable as PyIterable
from enum import Enum as PyEnum
from functools import wraps
from io import BufferedIOBase, IOBase
from types import FunctionType

from samarium.classes import (
    NULL,
    Array,
    Attrs,
    Enum,
    File,
    Iterator,
    Mode,
    Null,
    Num,
    Number,
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
    if isinstance(obj, (String, Number, Zip, File)):
        return obj.val
    if isinstance(obj, Null):
        return None
    if isinstance(obj, Array):
        return [to_python(i) for i in obj.val]
    if isinstance(obj, Table):
        return {to_python(k): to_python(v) for k, v in obj.val.items()}
    if isinstance(obj, Slice):
        return SliceRange(obj)
    if isinstance(obj, Enum):
        o = {k.removeprefix("sm_"): to_python(v) for k, v in obj.members.items()}
        return PyEnum(obj.name, o)
    if isinstance(obj, Iterator):
        return map(to_python, obj)
    raise TypeError(f"Conversion for type {type(obj).__name__!r} not found")


def to_samarium(obj: object) -> Attrs:
    if isinstance(obj, (int, bool, float)):
        return Num(obj)
    if isinstance(obj, str):
        return String(obj)
    if obj is None:
        return NULL
    if isinstance(obj, (list, tuple, set)):
        return Array([to_samarium(i) for i in obj])
    if isinstance(obj, dict):
        return Table({to_samarium(k): to_samarium(v) for k, v in obj.items()})
    if isinstance(obj, (range, slice)):
        return Slice(
            to_samarium(None if obj.start == 0 else obj.start),
            to_samarium(obj.stop),
            to_samarium(None if obj.step == 1 else obj.step),
        )
    if isinstance(obj, SliceRange):
        return obj._slice
    if isinstance(obj, IOBase):
        return File(
            obj, Mode(obj.mode).name, obj.name, binary=isinstance(obj, BufferedIOBase)  # type: ignore
        )
    if isinstance(obj, zip):
        return Zip(*obj)
    if isinstance(obj, type) and issubclass(obj, PyEnum):
        o = {f"sm_{k}": to_samarium(v) for k, v in obj.__members__.items()}
        return Enum(f"sm_{obj.__name__}", **o)
    if isinstance(obj, PyEnum):
        return to_samarium(obj.value)
    if isinstance(obj, PyIterable):
        return Iterator(obj)
    raise TypeError(f"Conversion for type {type(obj).__name__!r} not found")


def export(func: Callable) -> Callable[[Attrs], Attrs]:
    """Wraps a Python function to be used in Samarium"""

    @wraps(func)
    def wrapper(*_args: Attrs) -> Attrs:
        args = map(to_python, _args)
        return to_samarium(func(*args))

    if not isinstance(func, FunctionType):
        raise TypeError(f"cannot export a non-function type {type(func).__name__!r}")
    setattr(wrapper, f"__export_{wrapper}", True)

    return wrapper
