from __future__ import annotations

from enum import Enum
from functools import wraps
from secrets import choice
from typing import (
    Any, Callable, IO, Iterator, Tuple
)

from .exceptions import (
    NotDefinedError, SamariumSyntaxError,
    SamariumTypeError, SamariumValueError
)
from .utils import run_with_backup


def assert_smtype(function: Callable):
    @wraps(function)
    def wrapper(*args, **kwargs):
        args = [verify_type(arg) for arg in [*args, *kwargs.values()]]
        result = verify_type(function(*args))
        if isinstance(result, (Class, Callable, Module)):
            return result
        raise SamariumTypeError(
            f"invalid return type: {type(result).__name__}"
        )
    wrapper.type = Type(type(lambda: 0))
    wrapper.parent = Type(Class)
    return wrapper


def class_attributes(cls):
    cls.type = Type(Type)
    parents = [*cls.__bases__]
    cls.parent = (
        Type(parents[0])
        if len(parents) == 1
        else Array([Type(p) for p in parents])
    )
    return cls


def get_repr(obj: Class | Callable) -> str:
    if isinstance(obj, String):
        return f'"{obj._toString_()}"'
    elif hasattr(obj, "__name__"):
        return obj.__name__
    try:
        return obj._toString_().value
    except AttributeError:
        return str(obj)


def smhash(obj) -> Integer:
    return Integer(hash(str(hash(obj))))


def verify_type(obj: Any, *args) -> Class | Callable:
    if args:
        for i in [obj, *args]:
            verify_type(i)
    elif isinstance(obj, type):
        return Type(obj)
    elif isinstance(obj, (Class, Callable)):
        return obj
    elif isinstance(obj, tuple):
        return Array([*obj])
    elif isinstance(obj, type(None)):
        return Null()
    elif isinstance(obj, bool):
        return Integer(obj)
    elif isinstance(obj, type(i for i in [])):
        raise SamariumSyntaxError("invalid comprehension")
    raise SamariumTypeError(f"unknown type: {type(obj).__name__}")


class Class:

    def __init__(self, *args: Any, **kwargs: Any):
        self._create_(*args, **kwargs)

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
            self._notEquals_,
            lambda x: Integer(not self._equals_(x)),
            other
        )

    def __lt__(self, other: Class) -> Integer:
        return run_with_backup(
            self._lessThan_,
            lambda x: Integer(
                not self._greaterThan_(x)
                and not self._equals_(x)
            ),
            other
        )

    def __le__(self, other: Class) -> Integer:
        return run_with_backup(
            self._lessThanOrEqual_,
            lambda x: Integer(not self._greaterThan_(x)),
            other
        )

    def __gt__(self, other: Class) -> Integer:
        return self._greaterThan_(other)

    def __ge__(self, other: Class) -> Integer:
        return run_with_backup(
            self._greaterThanOrEqual_,
            lambda x: Integer(self._greaterThan_(x) or self._equals_(x)),
            other
        )

    @property
    def type(self) -> Type:
        return Type(self.__class__)

    @property
    def parent(self) -> Array | Type:
        parents = [*self.__class__.__bases__]
        if len(parents) == 1:
            return Type(parents[0])
        return Array([Type(p) for p in parents])

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


class Type(Class):

    def _create_(self, type_: type):
        self.value = type_

    def _equals_(self, other: Type) -> Integer:
        return Integer(self.value == other.value)

    def _toString_(self) -> String:
        return String(
            self
            .value
            .__name__
            .strip("_")
            .capitalize()
        )

    def _toBit_(self) -> Integer:
        return Integer(1)

    def _call_(self, *args) -> Class:
        if isinstance(lambda: 0, self.value):
            raise SamariumTypeError("cannot instantiate a function")
        return self.value(*(i.value for i in args))


class Slice(Class):

    def _create_(self, start: Any, stop: Any, step: Any):
        self.start = start
        self.stop = stop
        self.step = step
        tup = (start.value, stop.value, step.value)
        self.value = slice(*tup)
        self.range = range(*tup)

    def _random_(self) -> Integer:
        return Integer(choice(self.range))

    def is_empty(self) -> bool:
        return self.start == self.stop == self.step == Null()


class Null(Class):

    def _create_(self):
        self.value = None

    def _toString_(self) -> String:
        return String("null")

    def _hash_(self) -> Integer:
        return smhash(self.value)

    def _toBit_(self) -> Integer:
        return Integer(0)

    def _equals_(self, other: Null) -> Integer:
        return Integer(type(other) is Null)


class String(Class):

    def __str__(self) -> str:
        return self.value

    def _hash_(self) -> Integer:
        return smhash(self.value)

    def _cast_(self) -> Integer:
        if len(self.value) != 1:
            raise SamariumTypeError(
                f"cannot cast a string of length {len(self.value)}"
            )
        return Integer(ord(self.value))

    def _create_(self, value: Any):
        self.value = str(value)

    def _has_(self, element: String) -> Integer:
        return Integer(element.value in self.value)

    def _iterate_(self) -> Array:
        return Array([String(char) for char in self.value])

    def _random_(self) -> String:
        return String(choice(self.value))

    def _special_(self) -> Integer:
        return Integer(len(self.value))

    def _toBit_(self) -> Integer:
        return Integer(bool(self.value))

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
        return Integer(self.value == other.value)

    def _greaterThan_(self, other: String) -> Integer:
        return Integer(self.value > other.value)

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

    def _create_(self, value: Any):
        self.value = int(value)

    def _random_(self) -> Integer:
        if not self.value:
            return self
        elif self.value > 0:
            range_ = range(self.value)
        else:
            range_ = range(self.value, 0)
        return Integer(choice(range_))

    def _toBit_(self) -> Integer:
        return Integer(bool(self.value))

    def _toString_(self) -> String:
        return String(str(self.value))

    def _add_(self, other: Integer) -> Integer:
        return Integer(self.value + other.value)

    def _addAssign_(self, other: Integer) -> Integer:
        self = self._add_(other)
        return self

    def _subtract_(self, other: Integer) -> Integer:
        return Integer(self.value - other.value)

    def _subtractAssign_(self, other: Integer) -> Integer:
        self = self._subtract_(other)
        return self

    def _multiply_(self, other: Integer) -> Integer:
        return Integer(self.value * other.value)

    def _multiplyAssign_(self, other: Integer) -> Integer:
        self = self._multiply_(other)
        return self

    def _divide_(self, other: Integer) -> Integer:
        return Integer(self.value // other.value)

    def _divideAssign_(self, other: Integer) -> Integer:
        self = self._divide_(other)
        return self

    def _mod_(self, other: Integer) -> Integer:
        return Integer(self.value % other.value)

    def _modAssign_(self, other: Integer) -> Integer:
        self = self._mod_(other)
        return self

    def _power_(self, other: Integer) -> Integer:
        return Integer(self.value ** other.value)

    def _powerAssign_(self, other: Integer) -> Integer:
        self = self._power_(other)
        return self

    def _and_(self, other: Integer) -> Integer:
        return Integer(self.value & other.value)

    def _andAssign_(self, other: Integer) -> Integer:
        self = self._and_(other)
        return self

    def _or_(self, other: Integer) -> Integer:
        return Integer(self.value | other.value)

    def _orAssign_(self, other: Integer) -> Integer:
        self = self._or_(other)
        return self

    def _xor_(self, other: Integer) -> Integer:
        return Integer(self.value ^ other.value)

    def _xorAssign_(self, other: Integer) -> Integer:
        self = self._xor_(other)
        return self

    def _not_(self) -> Integer:
        return Integer(~self.value)

    def _negative_(self) -> Integer:
        return Integer(-self.value)

    def _positive_(self) -> Integer:
        return Integer(+self.value)

    def _equals_(self, other: Integer) -> Integer:
        return Integer(self.value == other.value)

    def _greaterThan_(self, other: Integer) -> Integer:
        return Integer(self.value > other.value)

    def _special_(self) -> String:
        return String(f"{self.value:b}")


class Table(Class):

    def _create_(self, value: dict[Any, Any]):
        self.value = {
            verify_type(k): verify_type(v)
            for k, v in value.items()
        }

    def _special_(self) -> Array:
        return Array([*self.value.values()])

    def _toString_(self) -> String:
        return String(
            "{{" + ", ".join(
                f"{get_repr(k)} -> {get_repr(v)}"
                for k, v in self.value.items()
            ) + "}}"
        )

    def _toBit_(self) -> Integer:
        return Integer(bool(self.value))

    def _getItem_(self, key: Any) -> Any:
        return self.value[key]

    def _setItem_(self, key: Any, value: Any):
        self.value[key] = value

    def _iterate_(self) -> Array:
        return Array([*self.value.keys()])

    def _random_(self) -> Any:
        if not self.value:
            raise SamariumValueError("table is empty")
        return choice([*self.value.keys()])

    def _has_(self, element: Any) -> Integer:
        return Integer(element in self.value)

    def _equals_(self, other: Table) -> Integer:
        return Integer(self.value == other.value)

    def _add_(self, other: Table) -> Table:
        return Table(self.value | other.value)

    def _addAssign_(self, other: Table) -> Table:
        self.value.update(other.value)
        return self

    def _subtract_(self, other: Class) -> Table:
        c = self.value.copy()
        del c[other]
        return Table(c)

    def _subtractAssign_(self, other: Class) -> Table:
        del self.value[other]
        return self


class Array(Class):

    def _create_(self, value: list[Any]):
        self.value = [verify_type(i) for i in value]

    def _special_(self) -> Integer:
        return Integer(len(self.value))

    def _toString_(self) -> String:
        return String(f"[{', '.join(get_repr(i) for i in self.value)}]")

    def _toBit_(self) -> Integer:
        return Integer(bool(self.value))

    def __iter__(self) -> Iterator:
        yield from self.value

    def _iterate_(self) -> Array:
        return self

    def _random_(self) -> Any:
        if not self.value:
            raise SamariumValueError("array is empty")
        return choice(self.value)

    def _has_(self, element: Any) -> Integer:
        return Integer(element in self.value)

    def _equals_(self, other: Array) -> Integer:
        return Integer(self.value == other.value)

    def _greaterThan_(self, other: Array) -> Integer:
        return Integer(self.value > other.value)

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
        with open(path.value, "x") as _:
            return Null()

    @staticmethod
    def open(
        path: String,
        mode: Mode,
        *, binary: bool = False
    ) -> Tuple[IO, bool]:
        f = open(path.value, mode.value + "b" * binary)
        return File(f, mode.name, path.value, binary)

    @staticmethod
    def open_binary(path: String, mode: Mode) -> tuple[IO, bool]:
        return FileManager.open(path, mode, binary=True)

    @staticmethod
    def quick(
        path: String | File,
        mode: Mode,
        *,
        data: String | None = None,
        binary: bool = False
    ) -> String | Array | None:
        if isinstance(path, String):
            with open(path.value, mode.value + "b" * binary) as f:
                if mode == Mode.READ:
                    if binary:
                        return Array([Integer(i) for i in f.read()])
                    return String(f.read())
                if data is None:
                    raise SamariumValueError("missing data")
                if isinstance(data, Array):
                    f.write(b"".join([
                        int(x).to_bytes(1, "big") for x in data.value
                    ]))
                else:
                    f.write(data.value)
        else:
            file = path
            if mode == Mode.READ:
                return file.load()
            if data is not None:
                file.save(data)
            else:
                raise SamariumValueError("missing data")
        return Null()


class File(Class):

    def _create_(self, file: IO, mode: str, path: str, binary: bool):
        self.binary = binary
        self.mode = mode
        self.path = path
        self.value = file

    def _toString_(self) -> String:
        return String(f"File(path:{self.path}, mode:{self.mode})")

    def _not_(self):
        self.value.close()
        return Null()

    def _getItem_(self, index: Integer | Slice) -> Array | String | Integer:
        if isinstance(index, Slice):
            if index.is_empty():
                return Integer(self.value.tell())
            if isinstance(index.step, Integer):
                raise SamariumValueError("cannot use step")
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
                    return Array([Integer(i) for i in data])
                return String(data)
            return self._getItem_(Slice(Integer(0), slice.stop, slice.step))
        else:
            self.value.seek(index.value)
            return Null()

    def load(self, bytes_: Integer | None = None) -> String | Array:
        if bytes_ is None:
            bytes_ = Integer(-1)
        val = self.value.read(bytes_.value)
        if self.binary:
            return Array([Integer(i) for i in val])
        return String(val)

    def save(self, data: String | Array):
        if (
            self.binary and isinstance(data, String)
            or not self.binary and isinstance(data, Array)
        ):
            raise SamariumTypeError(type(data).__name__)
        if isinstance(data, Array):
            self.value.write(b"".join([
                int(x).to_bytes(1, "big") for x in data.value
            ]))
        else:
            self.value.write(data.value)
        return Null()


class Module:

    def __init__(self, name: str, objects: dict[str, Class]):
        self.name = name
        self.objects = objects

    def __str__(self) -> String:
        return String(f"module '{self.name}'")

    def __getattr__(self, key: str) -> Class:
        return self.objects[key]
