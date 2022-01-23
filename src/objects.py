# type: ignore
from __future__ import annotations
from contextlib import suppress
from enum import Enum
from exceptions import (
    NotDefinedError, SamariumSyntaxError,
    SamariumTypeError, SamariumValueError
)
from typing import (
    Any, Callable, Dict, Iterator,
    IO, List, Optional, TypeVar, Tuple, Union
)

T = TypeVar("T")


def assert_smtype(function: Callable):
    def wrapper(*args, **kwargs):
        for i in [*args, *kwargs.values()]:
            verify_type(i)
        result = function(*args, **kwargs)
        if isinstance(result, (Class, Callable)):
            return result
        elif isinstance(result, tuple):
            return Array([*result])
        elif isinstance(result, type(None)):
            return Null()
        elif isinstance(result, bool):
            return Integer(int(result))
        else:
            raise SamariumTypeError(
                f"invalid return type: {type(result).__name__}"
            )
    return wrapper


def get_repr(obj: Class) -> str:
    if type(obj) is String:
        return f'"{obj.toString_()}"'
    return obj.toString_().value


def run_with_backup(
    main: Callable[..., T],
    backup: Callable[..., T],
    *args
) -> T:
    with suppress(NotDefinedError):
        return main(*args)
    return backup(*args)


def smhash(obj) -> Integer:
    return Integer(hash(str(hash(obj))))


def verify_type(obj: Any, *args):
    if args:
        for i in [obj, *args]:
            verify_type(i)
    elif isinstance(obj, (Class, Callable)):
        return obj
    elif isinstance(obj, tuple):
        raise SamariumSyntaxError("missing brackets")
    elif isinstance(obj, type(i for i in [])):
        raise SamariumSyntaxError("invalid comprehension")
    else:
        raise SamariumTypeError()


class Class:
    def __init__(self, *args: Any, **kwargs: Any):
        self.create_(*args, **kwargs)

    def __bool__(self) -> bool:
        return bool(self.toBit_().value)

    def __str__(self) -> str:
        return str(self.toString_().value)

    def __iter__(self) -> Iterator:
        return iter(self.iterate_().value)

    def __contains__(self, element: Any) -> Integer:
        return self.has_(element)

    def __call__(self, *args: Any) -> Any:
        return self.call_(*args)

    def __sizeof__(self) -> Integer:
        return self.size_() + Integer(1072)

    def __hash__(self) -> int:
        return self.hash_().value

    def __sub__(self, other: Class) -> Class:
        return self.subtract_(other)

    def __isub__(self, other: Class) -> Class:
        return self.subtractAssign_(other)

    def __add__(self, other: Class) -> Class:
        return self.add_(other)

    def __iadd__(self, other: Class) -> Class:
        return self.addAssign_(other)

    def __mul__(self, other: Class) -> Class:
        return self.multiply_(other)

    def __imul__(self, other: Class) -> Class:
        return self.multiplyAssign_(other)

    def __floordiv__(self, other: Class) -> Class:
        return self.divide_(other)

    def __ifloordiv__(self, other: Class) -> Class:
        return self.divideAssign_(other)

    def __mod__(self, other: Class) -> Class:
        return self.mod_(other)

    def __imod__(self, other: Class) -> Class:
        return self.modAssign_(other)

    def __pow__(self, other: Class) -> Class:
        return self.power_(other)

    def __ipow__(self, other: Class) -> Class:
        return self.powerAssign_(other)

    def __and__(self, other: Class) -> Class:
        return self.and_(other)

    def __iand__(self, other: Class) -> Class:
        return self.andAssign_(other)

    def __or__(self, other: Class) -> Class:
        return self.or_(other)

    def __ior__(self, other: Class) -> Class:
        return self.orAssign_(other)

    def __xor__(self, other: Class) -> Class:
        return self.xor_(other)

    def __ixor__(self, other: Class) -> Class:
        return self.xorAssign_(other)

    def __neg__(self) -> Class:
        return self.negative_()

    def __pos__(self) -> Class:
        return self.positive_()

    def __invert__(self) -> Class:
        return self.not_()

    def __getitem__(self, index: Integer) -> Any:
        return self.getItem_(index)

    def __setitem__(self, index: Integer, value: Any):
        return self.setItem_(index, value)

    def __getslice__(self, slice: Slice) -> Any:
        return self.getSlice_(slice)

    def __setslice__(self, slice: Slice, value: Any):
        return self.setSlice_(slice, value)

    def __eq__(self, other: Class) -> Integer:
        return self.equals_(other)

    def __ne__(self, other: Class) -> Integer:
        return run_with_backup(
            self.notEquals_,
            lambda x: Integer(not self.equals_(x)),
            other
        )

    def __lt__(self, other: Class) -> Integer:
        return run_with_backup(
            self.lessThan_,
            lambda x: Integer(
                not self.greaterThan_(x)
                and not self.equals_(x)
            ),
            other
        )

    def __le__(self, other: Class) -> Integer:
        return run_with_backup(
            self.lessThanOrEqual_,
            lambda x: Integer(not self.greaterThan_(x)),
            other
        )

    def __gt__(self, other: Class) -> Integer:
        return self.greaterThan_(other)

    def __ge__(self, other: Class) -> Integer:
        return run_with_backup(
            self.greaterThanOrEqual_,
            lambda x: Integer(self.greaterThan_(x) or self.equals_(x)),
            other
        )

    @property
    def type(self) -> String:
        return Type(self.__class__)

    @property
    def parent(self) -> Union[Array, Type]:
        parents = [*self.__class__.__bases__]
        if len(parents) == 1:
            return Type(parents[0])
        return Array([Type(p) for p in parents])

    def create_(self, *args: Any, **kwargs: Any):
        raise NotDefinedError(self, "create")

    def toBit_(self) -> Integer:
        raise NotDefinedError(self, "toBit")

    def toString_(self) -> String:
        raise NotDefinedError(self, "toString")

    def special_(self) -> Any:
        raise NotDefinedError(self, "special")

    def has_(self, element: Any) -> Integer:
        raise NotDefinedError(self, "has")

    def iterate_(self) -> Array:
        raise NotDefinedError(self, "iterate")

    def call_(self, *args: Any) -> Any:
        raise NotDefinedError(self, "call")

    def size_(self) -> Integer:
        raise NotDefinedError(self, "size")

    def hash_(self) -> Integer:
        raise NotDefinedError(self, "hash")

    def subtract_(self, other: Class) -> Class:
        raise NotDefinedError(self, "subtract")

    def subtractAssign_(self, other: Class) -> Class:
        raise NotDefinedError(self, "subtractAssign")

    def add_(self, other: Class) -> Class:
        raise NotDefinedError(self, "add")

    def addAssign_(self, other: Class) -> Class:
        raise NotDefinedError(self, "addAssign")

    def multiply_(self, other: Class) -> Class:
        raise NotDefinedError(self, "multiply")

    def multiplyAssign_(self, other: Class) -> Class:
        raise NotDefinedError(self, "multiplyAssign")

    def divide_(self, other: Class) -> Class:
        raise NotDefinedError(self, "divide")

    def divideAssign_(self, other: Class) -> Class:
        raise NotDefinedError(self, "divideAssign")

    def mod_(self, other: Class) -> Class:
        raise NotDefinedError(self, "mod")

    def modAssign_(self, other: Class) -> Class:
        raise NotDefinedError(self, "modAssign")

    def power_(self, other: Class) -> Class:
        raise NotDefinedError(self, "power")

    def powerAssign_(self, other: Class) -> Class:
        raise NotDefinedError(self, "powerAssign")

    def and_(self, other: Class) -> Class:
        raise NotDefinedError(self, "and")

    def andAssign_(self, other: Class) -> Class:
        raise NotDefinedError(self, "andAssign")

    def or_(self, other: Class) -> Class:
        raise NotDefinedError(self, "or")

    def orAssign_(self, other: Class) -> Class:
        raise NotDefinedError(self, "orAssign")

    def xor_(self, other: Class) -> Class:
        raise NotDefinedError(self, "xor")

    def xorAssign_(self, other: Class) -> Class:
        raise NotDefinedError(self, "xorAssign")

    def negative_(self) -> Class:
        raise NotDefinedError(self, "negative")

    def positive_(self) -> Class:
        raise NotDefinedError(self, "positive")

    def not_(self) -> Class:
        raise NotDefinedError(self, "not")

    def getItem_(self, index: Integer) -> Any:
        raise NotDefinedError(self, "getItem")

    def setItem_(self, index: Integer, value: Any):
        raise NotDefinedError(self, "setItem")

    def getSlice_(self, slice: Slice) -> Any:
        raise NotDefinedError(self, "getSlice")

    def setSlice_(self, slice: Slice, value: Any):
        raise NotDefinedError(self, "setSlice")

    def equals_(self, other: Class) -> Integer:
        raise NotDefinedError(self, "equals")

    def notEquals_(self, other: Class) -> Integer:
        raise NotDefinedError(self, "notEquals")

    def lessThan_(self, other: Class) -> Integer:
        raise NotDefinedError(self, "lessThan")

    def lessThanOrEqual_(self, other: Class) -> Integer:
        raise NotDefinedError(self, "lessThanOrEqual")

    def greaterThan_(self, other: Class) -> Integer:
        raise NotDefinedError(self, "greaterThan")

    def greaterThanOrEqual_(self, other: Class) -> Integer:
        raise NotDefinedError(self, "greaterThanOrEqual")

    def cast_(self):
        raise NotDefinedError(self, "cast")


class Type(Class):

    def create_(self, type_: type):
        self.value = type_

    def toString_(self) -> String:
        return String(
            self
            .value
            .__name__
            .capitalize()
            .rstrip("_")
        )

    def call_(self, *args) -> Class:
        return self.value(*args)


class Slice(Class):

    def create_(self, start: Any, stop: Any, step: Any):
        self.start = start or Null()
        self.stop = stop or Null()
        self.step = step or Null()
        self.value = slice(start.value, stop.value, step.value)

    def size_(self) -> Integer:
        return Integer(self.value.__sizeof__())

    def is_empty(self) -> bool:
        return self.start == self.stop == self.step == Null()

    def special_(self) -> Table:
        return Table({
            "start": self.start,
            "stop": self.stop,
            "step": self.step
        })

    def toString_(self) -> String:
        return String(f"Slice<<{self.start}, {self.stop}, {self.step}>>")


class Null(Class):

    def create_(self):
        self.value = None

    def toString_(self) -> String:
        return String("null")

    def hash_(self) -> Integer:
        return smhash(self.value)

    def size_(self) -> Integer:
        return Integer(self.value.__sizeof__())

    def toBit_(self) -> Integer:
        return Integer(0)

    def equals_(self, other: Null) -> Integer:
        return Integer(type(other) is Null)


class String(Class):

    def __str__(self) -> str:
        return self.value

    def hash_(self) -> Integer:
        return smhash(self.value)

    def cast_(self) -> Integer:
        if len(self.value) != 1:
            raise SamariumTypeError(
                f"cannot cast a string of length {len(self.value)}"
            )
        return Integer(ord(self.value))

    def create_(self, value: str):
        self.value = value

    def has_(self, element: String) -> Integer:
        return Integer(element.value in self.value)

    def iterate_(self) -> Array:
        return Array([String(char) for char in self.value])

    def size_(self) -> Integer:
        return Integer(self.value.__sizeof__())

    def special_(self) -> Integer:
        return Integer(len(self.value))

    def toBit_(self) -> Integer:
        return Integer(bool(self.value))

    def toString_(self) -> String:
        return self

    def add_(self, other: String) -> String:
        return String(self.value + other.value)

    def addAssign_(self, other: String) -> String:
        self = self.add_(other)
        return self

    def multiply_(self, times: Integer) -> String:
        return String(self.value * times.value)

    def multiplyAssign_(self, times: Integer) -> String:
        self = self.multiply_(times)
        return self

    def equals_(self, other: String) -> Integer:
        return Integer(self.value == other.value)

    def greaterThan_(self, other: String) -> Integer:
        return Integer(self.value > other.value)

    def getItem_(self, index: Integer) -> String:
        return String(self.value[index.value])

    def setItem_(self, index: Integer, value: String):
        string = [*self.value]
        string[index.value] = value.value
        self.value = "".join(string)

    def getSlice_(self, slice: Slice) -> String:
        return String(self.value[slice.value])

    def setSlice_(self, slice: Slice, value: String):
        string = [*self.value]
        string[slice.value] = value.value
        self.value = "".join(string)


class Integer(Class):

    def __int__(self) -> int:
        return self.value

    def cast_(self) -> String:
        return String(chr(self.value))

    def hash_(self) -> Integer:
        return smhash(self.value)

    def size_(self) -> Integer:
        return Integer(self.value.__sizeof__())

    def create_(self, value: int):
        self.value = int(value)

    def toBit_(self) -> Integer:
        return Integer(bool(self.value))

    def toString_(self) -> String:
        return String(str(self.value))

    def add_(self, other: Integer) -> Integer:
        return Integer(self.value + other.value)

    def addAssign_(self, other: Integer) -> Integer:
        self = self.add_(other)
        return self

    def subtract_(self, other: Integer) -> Integer:
        return Integer(self.value - other.value)

    def subtractAssign_(self, other: Integer) -> Integer:
        self = self.subtract_(other)
        return self

    def multiply_(self, other: Integer) -> Integer:
        return Integer(self.value * other.value)

    def multiplyAssign_(self, other: Integer) -> Integer:
        self = self.multiply_(other)
        return self

    def divide_(self, other: Integer) -> Integer:
        return Integer(self.value // other.value)

    def divideAssign_(self, other: Integer) -> Integer:
        self = self.divide_(other)
        return self

    def mod_(self, other: Integer) -> Integer:
        return Integer(self.value % other.value)

    def modAssign_(self, other: Integer) -> Integer:
        self = self.mod_(other)
        return self

    def power_(self, other: Integer) -> Integer:
        return Integer(self.value ** other.value)

    def powerAssign_(self, other: Integer) -> Integer:
        self = self.power_(other)
        return self

    def and_(self, other: Integer) -> Integer:
        return Integer(self.value & other.value)

    def andAssign_(self, other: Integer) -> Integer:
        self = self.and_(other)
        return self

    def or_(self, other: Integer) -> Integer:
        return Integer(self.value | other.value)

    def orAssign_(self, other: Integer) -> Integer:
        self = self.or_(other)
        return self

    def xor_(self, other: Integer) -> Integer:
        return Integer(self.value ^ other.value)

    def xorAssign_(self, other: Integer) -> Integer:
        self = self.xor_(other)
        return self

    def not_(self) -> Integer:
        return Integer(~self.value)

    def negative_(self) -> Integer:
        return Integer(-self.value)

    def positive_(self) -> Integer:
        return Integer(+self.value)

    def equals_(self, other: Integer) -> Integer:
        return Integer(self.value == other.value)

    def greaterThan_(self, other: Integer) -> Integer:
        return Integer(self.value > other.value)

    def special_(self) -> String:
        return String(f"{self.value:b}")


class Table(Class):

    def create_(self, value: Dict[Any, Any]):
        self.value = {
            type(verify_type(k))(k.value):
            type(verify_type(v))(v.value)
            for k, v in value.items()
        }

    def size_(self) -> Integer:
        return Integer(self.value.__sizeof__())

    def special_(self) -> Array:
        return Array([*self.value.values()])

    def toString_(self) -> String:
        return String(
            "{{" + ", ".join(
                f"{get_repr(k)} -> {get_repr(v)}"
                for k, v in self.value.items()
            ) + "}}"
        )

    def toBit_(self) -> Integer:
        return Integer(bool(self.value))

    def getItem_(self, key: Any) -> Any:
        return self.value[key]

    def setItem_(self, key: Any, value: Any):
        self.value[key] = value

    def iterate_(self) -> Array:
        return Array([*self.value.keys()])

    def has_(self, element: Any) -> Integer:
        return Integer(element in self.value)

    def equals_(self, other: Table) -> Integer:
        return Integer(self.value == other.value)

    def add_(self, other: Table) -> Table:
        return Table({**self.value, **other.value})

    def addAssign_(self, other: Table) -> Table:
        self.value.update(other.value)
        return self


class Array(Class):

    def create_(self, value: List[Any]):
        self.value = [
            type(verify_type(i))(i.value)
            for i in value
        ]

    def size_(self) -> Integer:
        return Integer(self.value.__sizeof__())

    def special_(self) -> Integer:
        return Integer(len(self.value))

    def toString_(self) -> String:
        return String(f"[{', '.join(get_repr(i) for i in self.value)}]")

    def toBit_(self) -> Integer:
        return Integer(bool(self.value))

    def __iter__(self) -> Iterator:
        yield from self.value

    def iterate_(self) -> Array:
        return self

    def has_(self, element: Any) -> Integer:
        return Integer(element in self.value)

    def equals_(self, other: Array) -> Integer:
        return Integer(self.value == other.value)

    def greaterThan_(self, other: Array) -> Integer:
        return Integer(self.value > other.value)

    def getItem_(self, index: Integer) -> Any:
        return self.value[index.value]

    def setItem_(self, index: Integer, value: Any):
        self.value[index.value] = value

    def getSlice_(self, slice: Slice) -> Array:
        return Array(self.value[slice.value])

    def setSlice_(self, slice: Slice, value: Any):
        self.value[slice.value] = value

    def add_(self, other: Array) -> Array:
        return Array(self.value + other.value)

    def addAssign_(self, other: Array) -> Array:
        self.value += other.value
        return self

    def subtract_(self, other: Union[Array, Integer]) -> Array:
        new_array = self.value.copy()
        if isinstance(other, Array):
            for i in other:
                new_array.remove(i)
        elif isinstance(other, Integer):
            new_array.pop(other.value)
        else:
            raise SamariumTypeError(type(other).__name__)
        return Array(new_array)

    def subtractAssign_(self, other: Union[Array, Integer]) -> Array:
        if isinstance(other, Array):
            for i in other:
                self.value.remove(i)
        elif isinstance(other, Integer):
            self.value.pop(other.value)
        else:
            raise SamariumTypeError(type(other).__name__)
        return self

    def multiply_(self, other: Integer) -> Array:
        return Array(self.value * other.value)

    def multiplyAssign_(self, other: Integer) -> Array:
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
            pass

    @staticmethod
    def open(
        path: String,
        mode: Mode,
        *, binary: bool = False
    ) -> Tuple[IO, bool]:
        f = open(path.value, mode.value + "b" * binary)
        return File(f, mode.name, path.value, binary)

    @staticmethod
    def open_binary(path: String, mode: Mode) -> Tuple[IO, bool]:
        return FileManager.open(path, mode, binary=True)

    @staticmethod
    def quick(
        path: Union[String, File],
        mode: Mode,
        *,
        data: Optional[String] = None,
        binary: bool = False
    ) -> Optional[Union[String, Array]]:
        if isinstance(path, String):
            with open(path.value, mode.value + "b" * binary) as f:
                if mode == Mode.READ:
                    if binary:
                        return Array([Integer(i) for i in f.read()])
                    return String(f.read())
                if data is not None:
                    if isinstance(data, Array):
                        f.write(b"".join([
                            int(x).to_bytes(1, "big") for x in data.value
                        ]))
                    else:
                        f.write(data.value)
                else:
                    raise SamariumValueError("missing data")
        else:
            file = path
            if mode == Mode.READ:
                return file.load()
            if data is not None:
                file.save(data)
            else:
                raise SamariumValueError("missing data")


class File(Class):

    def create_(self, file: IO, mode: str, path: str, binary: bool):
        self.binary = binary
        self.mode = mode
        self.path = path
        self.value = file

    def toString_(self) -> String:
        return String(f"File(path:{self.path}, mode:{self.mode})")

    def not_(self):
        self.value.close()

    def getSlice_(self, slice: Slice) -> Integer:
        if slice.is_empty():
            return Integer(self.value.tell())
        if isinstance(slice.step, Integer):
            raise SamariumValueError("cannot use step")
        if isinstance(slice.start, Integer):
            if not isinstance(slice.stop, Integer):
                return self.load(slice.start)
            current_position = self.value.tell()
            self.value.seek(slice.start.value)
            data = self.value.read(slice.stop.value - slice.start.value)
            if isinstance(data, bytes):
                data = [*data]
            self.value.seek(current_position)
            return data
        raise SamariumValueError("cannot use stop exclusively")

    def getItem_(self, index: Integer):
        self.value.seek(index.value)

    def load(self, bytes: Optional[Integer] = None) -> Union[String, Array]:
        if bytes is None:
            bytes = Integer(-1)
        val = self.value.read(bytes.value)
        return Array([Integer(i) for i in val]) if self.binary else String(val)

    def save(self, data: Union[String, Array]):
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
