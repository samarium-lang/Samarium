from __future__ import annotations
from contextlib import suppress
from exceptions import NotDefinedError, SamariumTypeError
from typing import Any, Callable, Iterator, TypeVar

T = TypeVar("T")


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


class Class:
    def __init__(self, *args: Any):
        self.create_(*args)

    def __bool__(self) -> bool:
        return bool(self.toBit_().value)

    def __str__(self) -> str:
        return str(self.toString_().value)

    def __iter__(self) -> Iterator:
        return iter(self.iterate_().array)

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

    def __iadd_(self, other: Class) -> Class:
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

    def create_(self, *args: Any):
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


class Slice(Class):

    def create_(self, value: slice):
        self.value = value
        self.start = value.start or Null()
        self.stop = value.stop or Null()
        self.step = value.step or Null()

    def size_(self) -> Integer:
        return Integer(self.value.__sizeof__())

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
        ...

    def toString_(self) -> String:
        return String("null")

    def hash_(self) -> Integer:
        return smhash(None)

    def size_(self) -> Integer:
        return Integer(None.__sizeof__())

    def toBit_(self) -> Integer:
        return Integer(0)

    def equals_(self, other: Null) -> Integer:
        return Integer(type(other) is Null)


class String(Class):

    def __str__(self) -> str:
        return self.value

    def hash_(self) -> Integer:
        return smhash(self.value)

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
        self.value += other.value
        return self

    def multiply_(self, times: Integer) -> String:
        return String(self.value * times.value)

    def multiplyAssign_(self, times: Integer) -> String:
        self.value *= times.value
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

    def hash_(self) -> Integer:
        return smhash(self.value)

    def size_(self) -> Integer:
        return Integer(self.value.__sizeof__())

    def create_(self, value: int):
        self.value = value

    def toBit_(self) -> Integer:
        return Integer(bool(self.value))

    def toString_(self) -> String:
        return String(str(self.value))

    def add_(self, other: Integer) -> Integer:
        return Integer(self.value + other.value)

    def addAssign_(self, other: Integer) -> Integer:
        self.value += other.value
        return self

    def subtract_(self, other: Integer) -> Integer:
        return Integer(self.value - other.value)

    def subtractAssign_(self, other: Integer) -> Integer:
        self.value -= other.value
        return self

    def multiply_(self, other: Integer) -> Integer:
        return Integer(self.value * other.value)

    def multiplyAssign_(self, other: Integer) -> Integer:
        self.value *= other.value
        return self

    def divide_(self, other: Integer) -> Integer:
        return Integer(self.value // other.value)

    def divideAssign_(self, other: Integer) -> Integer:
        self.value //= other.value
        return self

    def mod_(self, other: Integer) -> Integer:
        return Integer(self.value % other.value)

    def modAssign_(self, other: Integer) -> Integer:
        self.value %= other.value
        return self

    def power_(self, other: Integer) -> Integer:
        return Integer(self.value ** other.value)

    def powerAssign_(self, other: Integer) -> Integer:
        self.value **= other.value
        return self

    def and_(self, other: Integer) -> Integer:
        return Integer(self.value & other.value)

    def andAssign_(self, other: Integer) -> Integer:
        self.value &= other.value
        return self

    def or_(self, other: Integer) -> Integer:
        return Integer(self.value | other.value)

    def orAssign_(self, other: Integer) -> Integer:
        self.value |= other.value
        return self

    def xor_(self, other: Integer) -> Integer:
        return Integer(self.value ^ other.value)

    def xorAssign_(self, other: Integer) -> Integer:
        self.value ^= other.value
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

    def create_(self, table: dict[Any, Any]):
        self.table = table

    def size_(self) -> Integer:
        return Integer(self.table.__sizeof__())

    def special_(self) -> Array:
        return Array([*self.table.values()])

    def toString_(self) -> String:
        return String(
            "{{" + ", ".join(
                f"{get_repr(k)} -> {get_repr(v)}"
                for k, v in self.table.items()
            ) + "}}"
        )

    def toBit_(self) -> Integer:
        return Integer(bool(self.table))

    def getItem_(self, key: Any) -> Any:
        return self.table[key]

    def setItem_(self, key: Any, value: Any):
        self.table[key] = value

    def iterate_(self) -> Array:
        return Array([*self.table.keys()])

    def has_(self, element: Any) -> Integer:
        return Integer(element in self.table)

    def equals_(self, other: Table) -> Integer:
        return Integer(self.table == other.table)

    def add_(self, other: Table) -> Table:
        return Table(self.table | other.table)

    def addAssign_(self, other: Table) -> Table:
        self.table |= other.table
        return self


class Array(Class):

    def create_(self, array: list[Any]):
        self.array = array

    def size_(self) -> Integer:
        return Integer(self.array.__sizeof__())

    def special_(self) -> Integer:
        return Integer(len(self.array))

    def toString_(self) -> String:
        return String(f"[{', '.join(get_repr(i) for i in self.array)}]")

    def toBit_(self) -> Integer:
        return Integer(bool(self.array))

    def __iter__(self) -> Iterator:
        yield from self.array

    def iterate_(self) -> Array:
        return self

    def has_(self, element: Any) -> Integer:
        return Integer(element in self.array)

    def equals_(self, other: Array) -> Integer:
        return Integer(self.array == other.array)

    def greaterThan_(self, other: Array) -> Integer:
        return Integer(self.array > other.array)

    def getItem_(self, index: Integer) -> Any:
        return self.array[index.value]

    def setItem_(self, index: Integer, value: Any):
        self.array[index.value] = value

    def getSlice(self, slice: Slice) -> list[Any]:
        return self.array[slice.value]

    def setSlice(self, slice: Slice, value: Any):
        self.array[slice.value] = value

    def add_(self, other: Array) -> Array:
        return Array(self.array + other.array)

    def addAssign_(self, other: Array) -> Array:
        self.array += other.array
        return self

    def subtract_(self, other: Array | Integer) -> Array:
        new_array = self.array.copy()
        if isinstance(other, Array):
            for i in other:
                new_array.remove(i)
        elif isinstance(other, Integer):
            new_array.pop(other.value)
        else:
            raise SamariumTypeError(type(other).__name__)
        return Array(new_array)

    def subtractAssign_(self, other: Array | Integer) -> Array:
        if isinstance(other, Array):
            for i in other:
                self.array.remove(i)
        elif isinstance(other, Integer):
            self.array.pop(other.value)
        else:
            raise SamariumTypeError(type(other).__name__)
        return self

    def multiply_(self, other: Integer) -> Array:
        return Array(self.array * other.value)

    def multiplyAssign_(self, other: Integer) -> Array:
        self.array *= other.value
        return self
