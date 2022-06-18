from __future__ import annotations

import os

from collections.abc import Iterable
from contextlib import contextmanager, suppress
from enum import Enum
from functools import lru_cache, wraps
from inspect import signature
from secrets import choice, randbelow
from types import FunctionType, GeneratorType
from typing import Any, Callable, IO, Iterator, cast

from .exceptions import (
    NotDefinedError,
    SamariumIOError,
    SamariumSyntaxError,
    SamariumTypeError,
    SamariumValueError,
)
from .utils import get_callable_name, parse_integer, run_with_backup


def class_attributes(cls):
    cls.type = Type(Type)
    parents = cls.__bases__
    cls.parent = Type(parents[0]) if len(parents) == 1 else Array(map(Type, parents))
    return cls


def get_repr(obj: Class | Callable | Module) -> str:
    if isinstance(obj, String):
        return f'"{obj}"'
    return str(obj._toString_())


def smhash(obj) -> Integer:
    return Int(hash(str(hash(obj))))


def verify_type(obj: Any, *args) -> Class | Callable | Module:
    if args:
        for i in [obj, *args]:
            verify_type(i)
        return null
    elif isinstance(obj, type):
        return Type(obj)
    elif isinstance(obj, (Class, Callable, Module)):
        return obj
    elif isinstance(obj, tuple):
        return Array(obj)
    elif obj is None:
        return null
    elif isinstance(obj, bool):
        return Int(obj)
    elif isinstance(obj, GeneratorType):
        raise SamariumSyntaxError("invalid comprehension")
    else:
        raise SamariumTypeError(f"unknown type: {type(obj).__name__}")


class Class:
    __slots__ = ("value",)

    def __init__(self, *args: Any):
        with suppress(NotDefinedError):
            self._create_(*args)

    def __bool__(self) -> bool:
        return bool(self._toBit_().value)

    def __str__(self) -> str:
        return str(self._toString_().value)

    def __iter__(self) -> Iterator:
        return iter(self._iterate_().value)

    def __contains__(self, element: Any) -> Integer:
        return self._has_(element)

    def __call__(self, *args: Any) -> Any:
        return self._call_(*args)

    def __hash__(self) -> int:
        return self._hash_().value

    def __sub__(self, other: Class) -> Class:
        return self._subtract_(other)

    def __isub__(self, other: Class) -> Class:
        return self._subtractAssign_(other)

    def __add__(self, other: Class) -> Class:
        return self._add_(other)

    def __iadd__(self, other: Class) -> Class:
        return self._addAssign_(other)

    def __mul__(self, other: Class) -> Class:
        return self._multiply_(other)

    def __imul__(self, other: Class) -> Class:
        return self._multiplyAssign_(other)

    def __floordiv__(self, other: Class) -> Class:
        return self._divide_(other)

    def __ifloordiv__(self, other: Class) -> Class:
        return self._divideAssign_(other)

    def __mod__(self, other: Class) -> Class:
        return self._mod_(other)

    def __imod__(self, other: Class) -> Class:
        return self._modAssign_(other)

    def __pow__(self, other: Class) -> Class:
        return self._power_(other)

    def __ipow__(self, other: Class) -> Class:
        return self._powerAssign_(other)

    def __and__(self, other: Class) -> Class:
        return self._and_(other)

    def __iand__(self, other: Class) -> Class:
        return self._andAssign_(other)

    def __or__(self, other: Class) -> Class:
        return self._or_(other)

    def __ior__(self, other: Class) -> Class:
        return self._orAssign_(other)

    def __xor__(self, other: Class) -> Class:
        return self._xor_(other)

    def __ixor__(self, other: Class) -> Class:
        return self._xorAssign_(other)

    def __neg__(self) -> Class:
        return self._negative_()

    def __pos__(self) -> Class:
        return self._positive_()

    def __invert__(self) -> Class:
        return self._not_()

    def __getitem__(self, index: Integer | Slice) -> Any:
        return self._getItem_(index)

    def __setitem__(self, index: Integer | Slice, value: Any):
        return self._setItem_(index, value)

    def __eq__(self, other: Class) -> Integer:
        return self._equals_(other)

    def __ne__(self, other: Class) -> Integer:
        return run_with_backup(
            self._notEquals_, lambda x: Int(not self._equals_(x)), other
        )

    def __lt__(self, other: Class) -> Integer:
        return run_with_backup(
            self._lessThan_,
            lambda x: Int(not (self._greaterThan_(x) or self._equals_(x))),
            other,
        )

    def __le__(self, other: Class) -> Integer:
        return run_with_backup(
            self._lessThanOrEqual_, lambda x: Int(not self._greaterThan_(x)), other
        )

    def __gt__(self, other: Class) -> Integer:
        return self._greaterThan_(other)

    def __ge__(self, other: Class) -> Integer:
        return run_with_backup(
            self._greaterThanOrEqual_,
            lambda x: Int(self._greaterThan_(x) or self._equals_(x)),
            other,
        )

    @property
    def type(self) -> Type:
        return Type(type(self))

    @property
    def parent(self) -> Array | Type:
        parents = type(self).__bases__
        if len(parents) == 1:
            return Type(parents[0])
        return Array(map(Type, parents))

    def _create_(self, *args: Any, **kwargs: Any):
        raise NotDefinedError(self, "create")

    def _toBit_(self) -> Integer:
        raise NotDefinedError(self, "toBit")

    def _toString_(self) -> String:
        raise NotDefinedError(self, "toString")

    def _special_(self) -> Any:
        raise NotDefinedError(self, "special")

    def _has_(self, element: Any) -> Integer:
        raise NotDefinedError(self, "has")

    def _iterate_(self) -> Array:
        raise NotDefinedError(self, "iterate")

    def _call_(self, *args: Any) -> Any:
        raise NotDefinedError(self, "call")

    def _hash_(self) -> Integer:
        raise NotDefinedError(self, "hash")

    def _subtract_(self, other: Class) -> Class:
        raise NotDefinedError(self, "subtract")

    def _subtractAssign_(self, other: Class) -> Class:
        raise NotDefinedError(self, "subtractAssign")

    def _add_(self, other: Class) -> Class:
        raise NotDefinedError(self, "add")

    def _addAssign_(self, other: Class) -> Class:
        raise NotDefinedError(self, "addAssign")

    def _multiply_(self, other: Class) -> Class:
        raise NotDefinedError(self, "multiply")

    def _multiplyAssign_(self, other: Class) -> Class:
        raise NotDefinedError(self, "multiplyAssign")

    def _divide_(self, other: Class) -> Class:
        raise NotDefinedError(self, "divide")

    def _divideAssign_(self, other: Class) -> Class:
        raise NotDefinedError(self, "divideAssign")

    def _mod_(self, other: Class) -> Class:
        raise NotDefinedError(self, "mod")

    def _modAssign_(self, other: Class) -> Class:
        raise NotDefinedError(self, "modAssign")

    def _power_(self, other: Class) -> Class:
        raise NotDefinedError(self, "power")

    def _powerAssign_(self, other: Class) -> Class:
        raise NotDefinedError(self, "powerAssign")

    def _and_(self, other: Class) -> Class:
        raise NotDefinedError(self, "and")

    def _andAssign_(self, other: Class) -> Class:
        raise NotDefinedError(self, "andAssign")

    def _or_(self, other: Class) -> Class:
        raise NotDefinedError(self, "or")

    def _orAssign_(self, other: Class) -> Class:
        raise NotDefinedError(self, "orAssign")

    def _xor_(self, other: Class) -> Class:
        raise NotDefinedError(self, "xor")

    def _xorAssign_(self, other: Class) -> Class:
        raise NotDefinedError(self, "xorAssign")

    def _negative_(self) -> Class:
        raise NotDefinedError(self, "negative")

    def _positive_(self) -> Class:
        raise NotDefinedError(self, "positive")

    def _not_(self) -> Class:
        raise NotDefinedError(self, "not")

    def _getItem_(self, index: Integer | Slice) -> Any:
        raise NotDefinedError(self, "getItem")

    def _setItem_(self, index: Integer | Slice, value: Any):
        raise NotDefinedError(self, "setItem")

    def _equals_(self, other: Class) -> Integer:
        raise NotDefinedError(self, "equals")

    def _notEquals_(self, other: Class) -> Integer:
        raise NotDefinedError(self, "notEquals")

    def _lessThan_(self, other: Class) -> Integer:
        raise NotDefinedError(self, "lessThan")

    def _lessThanOrEqual_(self, other: Class) -> Integer:
        raise NotDefinedError(self, "lessThanOrEqual")

    def _greaterThan_(self, other: Class) -> Integer:
        raise NotDefinedError(self, "greaterThan")

    def _greaterThanOrEqual_(self, other: Class) -> Integer:
        raise NotDefinedError(self, "greaterThanOrEqual")

    def _cast_(self):
        raise NotDefinedError(self, "cast")

    def _random_(self):
        raise NotDefinedError(self, "random")


@contextmanager
def modify(func: Callable, args: list[Any], argc: int):
    if func.__code__.co_flags != 71:
        yield func, args
        return
    x = argc - 1
    args = [*args[:x], Array(args[x:])]
    func.__code__ = func.__code__.replace(co_flags=71, co_argcount=argc - 1)
    args *= argc > 0
    yield func, args


def function(func: Callable):
    @wraps(func)
    def wrapper(*args):
        args = [*map(verify_type, args)]
        with modify(func, args, argc) as (f, args):
            result = verify_type(f(*args))
        if isinstance(result, (Class, Callable, Module)):
            return result
        raise SamariumTypeError(f"invalid return type: {type(result).__name__}")

    argc = len(signature(func).parameters)

    wrapper._toString_ = lambda: String(get_callable_name(func))
    wrapper._special_ = lambda: Int(argc)
    wrapper.argc = argc
    wrapper.parent = Type(Class)
    wrapper.type = Type(FunctionType)

    return wrapper

class Type(Class):
    def _create_(self, type_: type):
        self.value = type_

    def _equals_(self, other: Type) -> Integer:
        return Int(self.value == other.value)

    def _notEquals_(self, other: Type) -> Integer:
        return Int(self.value != other.value)

    def _toString_(self) -> String:
        if self.value is FunctionType:
            return String("Function")
        return String(get_callable_name(self.value))

    def _toBit_(self) -> Integer:
        return Int(1)

    def _call_(self, *args) -> Class:
        if self.value is FunctionType:
            raise SamariumTypeError("cannot instantiate a function")
        if self.value is Module:
            raise SamariumTypeError("cannot instantiate a module")
        return self.value(*args)


class Slice(Class):
    __slots__ = ("start", "stop", "step", "tup", "value")

    def _create_(self, start: Any, stop: Any, step: Any):
        self.start = start
        self.stop = stop
        self.step = step
        self.tup = start.value, stop.value, step.value
        self.value = slice(*self.tup)

    def _random_(self) -> Integer:
        if self.stop is None:
            raise SamariumValueError(
                "cannot generate a random value for slice with null stop"
            )
        tup = self.tup[0] or 0, self.tup[1], self.tup[2] or 1
        range_ = range(*tup)
        return Int(choice(range_))

    def is_empty(self) -> bool:
        return self.start == self.stop == self.step == null

    def _toString_(self) -> String:
        start, stop, step = self.tup
        if start is stop is step is None:
            return String("<<>>")
        string = ""
        if start is not None:
            string += get_repr(start)
            if stop is step is None:
                string += ".."
        if stop is not None:
            string += f"..{get_repr(stop)}"
        if step is not None:
            string += f"**{get_repr(step)}"
        return String(f"<<{string}>>")

    def _equals_(self, other: Slice) -> Integer:
        return Int(self.tup == other.tup)

    def _notEquals_(self, other: Slice) -> Integer:
        return Int(self.tup != other.tup)


class Null(Class):
    def _create_(self):
        self.value = None

    def _toString_(self) -> String:
        return String("null")

    def _hash_(self) -> Integer:
        return smhash(self.value)

    def _toBit_(self) -> Integer:
        return Int(0)

    def _equals_(self, other: Null) -> Integer:
        return Int(type(other) is Null)

    def _notEquals_(self, other: Null) -> Integer:
        return Int(type(other) is not Null)


null = Null()


class String(Class):
    def __str__(self) -> str:
        return self.value

    def _hash_(self) -> Integer:
        return smhash(self.value)

    def _cast_(self) -> Integer:
        if len(self.value) != 1:
            raise SamariumTypeError(f"cannot cast a string of length {len(self.value)}")
        return Int(ord(self.value))

    def _create_(self, value: Any = ""):
        self.value = str(value)

    def _has_(self, element: String) -> Integer:
        return Int(element.value in self.value)

    def _iterate_(self) -> Array:
        return Array(map(String, self.value))

    def _random_(self) -> String:
        return String(choice(self.value))

    def _special_(self) -> Integer:
        return Int(len(self.value))

    def _toBit_(self) -> Integer:
        return Int(self.value != "")

    def _toString_(self) -> String:
        return self

    def _add_(self, other: String) -> String:
        return String(self.value + other.value)

    def _addAssign_(self, other: String) -> String:
        self = self._add_(other)
        return self

    def _multiply_(self, times: Integer) -> String:
        return String(self.value * times.value)

    def _multiplyAssign_(self, times: Integer) -> String:
        self = self._multiply_(times)
        return self

    def _equals_(self, other: String) -> Integer:
        return Int(self.value == other.value)

    def _notEquals_(self, other: String) -> Integer:
        return Int(self.value != other.value)

    def _greaterThan_(self, other: String) -> Integer:
        return Int(self.value > other.value)

    def _lessThan_(self, other: String) -> Integer:
        return Int(self.value < other.value)

    def _greaterThanOrEqual_(self, other: String) -> Integer:
        return Int(self.value >= other.value)

    def _lessThanOrEqual_(self, other: String) -> Integer:
        return Int(self.value <= other.value)

    def _getItem_(self, index: Integer | Slice) -> String:
        return String(self.value[index.value])

    def _setItem_(self, index: Integer | Slice, value: String):
        string = [*self.value]
        string[index.value] = value.value
        self.value = "".join(string)


class Integer(Class):
    def __int__(self) -> int:
        return self.value

    def _cast_(self) -> String:
        return String(chr(self.value))

    def _hash_(self) -> Integer:
        return smhash(self.value)

    def _create_(self, value: Any = None):
        t = type(value)
        if hasattr(value, "value"):
            value = value.value
        if isinstance(value, (int, bool, float)):
            self.value = int(value)
        elif value is None:
            self.value = 0
        elif isinstance(value, str):
            self.value = parse_integer(value)
        else:
            raise SamariumTypeError(f"cannot cast {t.__name__} to Integer")

    def _random_(self) -> Integer:
        v = self.value
        if not v:
            return self
        elif v > 0:
            return Int(randbelow(v))
        else:
            return Int(-randbelow(v) - 1)

    def _toBit_(self) -> Integer:
        return Int(self.value != 0)

    def _toString_(self) -> String:
        return String(str(self.value))

    def _add_(self, other: Integer) -> Integer:
        return Int(self.value + other.value)

    def _addAssign_(self, other: Integer) -> Integer:
        self = self._add_(other)
        return self

    def _subtract_(self, other: Integer) -> Integer:
        return Int(self.value - other.value)

    def _subtractAssign_(self, other: Integer) -> Integer:
        self = self._subtract_(other)
        return self

    def _multiply_(self, other: Integer) -> Integer:
        return Int(self.value * other.value)

    def _multiplyAssign_(self, other: Integer) -> Integer:
        self = self._multiply_(other)
        return self

    def _divide_(self, other: Integer) -> Integer:
        return Int(self.value // other.value)

    def _divideAssign_(self, other: Integer) -> Integer:
        self = self._divide_(other)
        return self

    def _mod_(self, other: Integer) -> Integer:
        return Int(self.value % other.value)

    def _modAssign_(self, other: Integer) -> Integer:
        self = self._mod_(other)
        return self

    def _power_(self, other: Integer) -> Integer:
        return Int(self.value ** other.value)

    def _powerAssign_(self, other: Integer) -> Integer:
        self = self._power_(other)
        return self

    def _and_(self, other: Integer) -> Integer:
        return Int(self.value & other.value)

    def _andAssign_(self, other: Integer) -> Integer:
        self = self._and_(other)
        return self

    def _or_(self, other: Integer) -> Integer:
        return Int(self.value | other.value)

    def _orAssign_(self, other: Integer) -> Integer:
        self = self._or_(other)
        return self

    def _xor_(self, other: Integer) -> Integer:
        return Int(self.value ^ other.value)

    def _xorAssign_(self, other: Integer) -> Integer:
        self = self._xor_(other)
        return self

    def _not_(self) -> Integer:
        return Int(~self.value)

    def _negative_(self) -> Integer:
        return Int(-self.value)

    def _positive_(self) -> Integer:
        return Int(+self.value)

    def _equals_(self, other: Integer) -> Integer:
        return Int(self.value == other.value)

    def _notEquals_(self, other: Integer) -> Integer:
        return Int(self.value != other.value)

    def _greaterThan_(self, other: Integer) -> Integer:
        return Int(self.value > other.value)

    def _lessThan_(self, other: Integer) -> Integer:
        return Int(self.value < other.value)

    def _greaterThanOrEqual_(self, other: Integer) -> Integer:
        return Int(self.value >= other.value)

    def _lessThanOrEqual_(self, other: Integer) -> Integer:
        return Int(self.value <= other.value)

    def _special_(self) -> String:
        return String(f"{self.value:b}")


Int = lru_cache(1024)(Integer)


class Table(Class):
    def _create_(self, value: Any = None):
        if value is None:
            self.value = {}
        elif isinstance(value, Table):
            self.value = value.value.copy()
        elif isinstance(value, dict):
            self.value = {verify_type(k): verify_type(v) for k, v in value.items()}
        elif isinstance(value, Array):
            arr = value.value
            if all(isinstance(i, (String, Array)) and len(i.value) == 2 for i in arr):
                table: dict[Class, Class] = {}
                for e in arr:
                    if isinstance(e, String):
                        k, v = e.value
                        table[String(k)] = String(v)
                    else:
                        k, v = cast(Array, e)
                        table[k] = v
                self.value = Table(table).value
        else:
            raise SamariumTypeError(f"cannot cast {type(value).__name__} to Table")

    def _special_(self) -> Array:
        return Array(self.value.values())

    def _toString_(self) -> String:
        return String(
            "{{"
            + ", ".join(
                f"{get_repr(k)} -> {get_repr(v)}" for k, v in self.value.items()
            )
            + "}}"
        )

    def _toBit_(self) -> Integer:
        return Int(self.value != {})

    def _getItem_(self, key: Any) -> Any:
        try:
            return self.value[key]
        except KeyError:
            raise SamariumValueError(f"key not found: {key}")

    def _setItem_(self, key: Any, value: Any):
        self.value[key] = value

    def _iterate_(self) -> Array:
        return Array(self.value.keys())

    def _random_(self) -> Any:
        if not self.value:
            raise SamariumValueError("table is empty")
        return choice([*self.value.keys()])

    def _has_(self, element: Any) -> Integer:
        return Int(element in self.value)

    def _equals_(self, other: Table) -> Integer:
        return Int(self.value == other.value)

    def _notEquals_(self, other: Table) -> Integer:
        return Int(self.value == other.value)

    def _add_(self, other: Table) -> Table:
        return Table(self.value | other.value)

    def _addAssign_(self, other: Table) -> Table:
        self.value.update(other.value)
        return self

    def _subtract_(self, other: Class) -> Table:
        c = self.value.copy()
        try:
            del c[other]
        except KeyError:
            raise SamariumValueError(f"key not found: {other}")
        return Table(c)

    def _subtractAssign_(self, other: Class) -> Table:
        try:
            del self.value[other]
        except KeyError:
            raise SamariumValueError(f"key not found: {other}")
        return self


class Array(Class):
    def _create_(self, value: Any = None):
        if value is None:
            self.value = []
        elif isinstance(value, Array):
            self.value = value.value.copy()
        elif isinstance(value, String):
            self.value = Array(map(String, value.value)).value
        elif isinstance(value, Table):
            self.value = Array(map(Array, value.value.items())).value
        elif isinstance(value, Iterable):
            self.value = [*map(verify_type, value)]
        else:
            raise SamariumTypeError(f"cannot cast {type(value).__name__} to Array")

    def _special_(self) -> Integer:
        return Int(len(self.value))

    def _toString_(self) -> String:
        return String(f"[{', '.join(map(get_repr, self.value))}]")

    def _toBit_(self) -> Integer:
        return Int(self.value != [])

    def __iter__(self) -> Iterator:
        yield from self.value

    def _iterate_(self) -> Array:
        return self

    def _random_(self) -> Any:
        if not self.value:
            raise SamariumValueError("array is empty")
        return choice(self.value)

    def _has_(self, element: Any) -> Integer:
        return Int(element in self.value)

    def _equals_(self, other: Array) -> Integer:
        return Int(self.value == other.value)

    def _notEquals_(self, other: Array) -> Integer:
        return Int(self.value != other.value)

    def _greaterThan_(self, other: Array) -> Integer:
        return Int(self.value > other.value)

    def _lessThan_(self, other: Array) -> Integer:
        return Int(self.value < other.value)

    def _greaterThanOrEqual_(self, other: Array) -> Integer:
        return Int(self.value >= other.value)

    def _lessThanOrEqual_(self, other: Array) -> Integer:
        return Int(self.value <= other.value)

    def _getItem_(self, index: Integer | Slice) -> Any:
        if isinstance(index, Integer):
            return self.value[index.value]
        return Array(self.value[index.value])

    def _setItem_(self, index: Integer | Slice, value: Any):
        self.value[index.value] = value

    def _add_(self, other: Array) -> Array:
        return Array(self.value + other.value)

    def _addAssign_(self, other: Array) -> Array:
        self.value += other.value
        return self

    def _subtract_(self, other: Array | Integer) -> Array:
        new_array = self.value.copy()
        if isinstance(other, Array):
            for i in other:
                new_array.remove(i)
        elif isinstance(other, Integer):
            new_array.pop(other.value)
        else:
            raise SamariumTypeError(type(other).__name__)
        return Array(new_array)

    def _subtractAssign_(self, other: Array | Integer) -> Array:
        if isinstance(other, Array):
            for i in other:
                self.value.remove(i)
        elif isinstance(other, Integer):
            self.value.pop(other.value)
        else:
            raise SamariumTypeError(type(other).__name__)
        return self

    def _multiply_(self, other: Integer) -> Array:
        return Array(self.value * other.value)

    def _multiplyAssign_(self, other: Integer) -> Array:
        self.value *= other.value
        return self


class Mode(Enum):
    READ = "r"
    WRITE = "w"
    READ_WRITE = "r+"
    APPEND = "a"


class FileManager:
    @staticmethod
    def create(path: String):
        open(path.value, "x").close()
        return null

    @staticmethod
    def open(path: String | Integer, mode: Mode, *, binary: bool = False) -> File:
        if isinstance(path, Integer) and mode is Mode.READ_WRITE:
            raise SamariumIOError(
                "cannot open a standard stream in a read & write mode"
            )
        f = open(path.value, mode.value + "b" * binary)
        return File(f, mode.name, path.value, binary)

    @staticmethod
    def open_binary(path: String, mode: Mode) -> File:
        return FileManager.open(path, mode, binary=True)

    @staticmethod
    def quick(
        path: String | File,
        mode: Mode,
        *,
        data: String | Array | None = None,
        binary: bool = False,
    ) -> String | Array | Null:
        if isinstance(path, String):
            with open(path.value, mode.value + "b" * binary) as f:
                if mode is Mode.READ:
                    if binary:
                        return Array(map(Int, f.read()))
                    return String(f.read())
                if data is None:
                    raise SamariumIOError("missing data")
                if isinstance(data, Array):
                    f.write(b"".join(x.value.to_bytes(1, "big") for x in data.value))
                else:
                    f.write(data.value)
        elif isinstance(path, Integer):
            if mode in {Mode.APPEND, Mode.WRITE}:
                fd = cast(int, path.value)
                os.write(fd, str(data).encode())
            else:
                raise SamariumIOError(
                    "reading from file descriptors is "
                    "not supported for quick operations"
                )
        else:
            file = path
            if mode is Mode.READ:
                return file.load()
            if data is not None:
                file.save(data)
            else:
                raise SamariumIOError("missing data")
        return null


class File(Class):
    __slots__ = ("binary", "mode", "path", "value")

    def _create_(self, file: IO, mode: str, path: str, binary: bool):
        self.binary = binary
        self.mode = mode
        self.path = path
        self.value = file

    def _toString_(self) -> String:
        return String(f"File(path:{self.path}, mode:{self.mode})")

    def _not_(self):
        self.value.close()
        return null

    def _getItem_(self, index: Integer | Slice) -> Array | String | Integer | Null:
        if isinstance(index, Slice):
            if index.is_empty():
                return Int(self.value.tell())
            if isinstance(index.step, Integer):
                raise SamariumIOError("cannot use step")
            if isinstance(index.start, Integer):
                if not isinstance(index.stop, Integer):
                    return self.load(index.start)
                current_position = self.value.tell()
                self.value.seek(index.start.value)
                data = self.value.read(index.stop.value - index.start.value)
                self.value.seek(current_position)
                if self.binary:
                    if isinstance(data, bytes):
                        data = [*data]
                    return Array(map(Int, data))
                return String(data)
            return self[Slice(Int(0), slice.stop, slice.step)]
        else:
            self.value.seek(index.value)
            return null

    def load(self, bytes_: Integer | None = None) -> String | Array:
        if bytes_ is None:
            bytes_ = Int(-1)
        val = self.value.read(cast(Integer, bytes_).value)
        if self.binary:
            return Array(map(Int, val))
        return String(val)

    def save(self, data: String | Array):
        if (self.binary and isinstance(data, String)) or (
            not self.binary and isinstance(data, Array)
        ):
            raise SamariumTypeError(type(data).__name__)
        if isinstance(data, Array):
            self.value.write(b"".join(x.value.to_bytes(1, "big") for x in data.value))
        else:
            self.value.write(data.value)
        return null


class Module:
    __slots__ = ("name", "objects")

    def __init__(self, name: str, objects: dict[str, Class]):
        self.name = name
        self.objects = objects

    def __str__(self) -> str:
        return f"module '{self.name}'"

    def __getattr__(self, key: str) -> Class:
        return self.objects[key]

    @property
    def type(self) -> Type:
        return Type(type(self))
