from __future__ import annotations

import os

from collections.abc import Iterable
from contextlib import contextmanager, suppress
from enum import Enum
from functools import lru_cache, wraps
from inspect import signature
from re import compile
from secrets import choice, randbelow
from types import FunctionType, GeneratorType
from typing import Any, Callable, IO, Iterator as Iter, cast

from .exceptions import (
    NotDefinedError,
    SamariumIOError,
    SamariumSyntaxError,
    SamariumTypeError,
    SamariumValueError,
)
from .utils import get_callable_name, parse_integer, run_with_backup


I64_MAX = 9223372036854775807


class MISSING:
    def __getattr__(self, _):
        raise SamariumValueError("cannot use the MISSING object")


class Class:
    __slots__ = ("value",)

    def __init__(self, *args: Any):
        with suppress(NotDefinedError):
            self.sm_create(*args)

    def __bool__(self) -> bool:
        return bool(self.sm_to_bit().value)

    def __str__(self) -> str:
        return str(self.sm_to_string().value)

    def __iter__(self) -> Iter:
        return iter(self.sm_iterate().value)

    def __contains__(self, element: Any) -> Integer:
        return self.sm_has(element)

    def __call__(self, *args: Any) -> Any:
        return self.sm_call(*args)

    def __hash__(self) -> int:
        return self.sm_hash().value

    def __sub__(self, other: Class) -> Class:
        return self.sm_subtract(other)

    def __isub__(self, other: Class) -> Class:
        return self.sm_subtract_assign(other)

    def __add__(self, other: Class) -> Class:
        return self.sm_add(other)

    def __iadd__(self, other: Class) -> Class:
        return self.sm_add_assign(other)

    def __mul__(self, other: Class) -> Class:
        return self.sm_multiply(other)

    def __imul__(self, other: Class) -> Class:
        return self.sm_multiply_assign(other)

    def __floordiv__(self, other: Class) -> Class:
        return self.sm_divide(other)

    def __ifloordiv__(self, other: Class) -> Class:
        return self.sm_divide_assign(other)

    def __mod__(self, other: Class) -> Class:
        return self.sm_mod(other)

    def __imod__(self, other: Class) -> Class:
        return self.sm_mod_assign(other)

    def __pow__(self, other: Class) -> Class:
        return self.sm_power(other)

    def __ipow__(self, other: Class) -> Class:
        return self.sm_power_assign(other)

    def __and__(self, other: Class) -> Class:
        return self.sm_and(other)

    def __iand__(self, other: Class) -> Class:
        return self.sm_and_assign(other)

    def __or__(self, other: Class) -> Class:
        return self.sm_or(other)

    def __ior__(self, other: Class) -> Class:
        return self.sm_or_assign(other)

    def __xor__(self, other: Class) -> Class:
        return self.sm_xor(other)

    def __ixor__(self, other: Class) -> Class:
        return self.sm_xor_assign(other)

    def __neg__(self) -> Class:
        return self.sm_negative()

    def __pos__(self) -> Class:
        return self.sm_positive()

    def __invert__(self) -> Class:
        return self.sm_not()

    def __getitem__(self, index: Integer | Slice) -> Any:
        return self.sm_get_item(index)

    def __setitem__(self, index: Integer | Slice, value: Any):
        return self.sm_set_item(index, value)

    def __eq__(self, other: Class) -> Integer:
        return self.sm_equals(other)

    def __ne__(self, other: Class) -> Integer:
        return run_with_backup(
            self.sm_not_equals, lambda x: Int(not self.sm_equals(x)), other
        )

    def __lt__(self, other: Class) -> Integer:
        return run_with_backup(
            self.sm_less_than,
            lambda x: Int(not (self.sm_greater_than(x) or self.sm_equals(x))),
            other,
        )

    def __le__(self, other: Class) -> Integer:
        return run_with_backup(
            self.sm_less_than_or_equal,
            lambda x: Int(not self.sm_greater_than(x)),
            other,
        )

    def __gt__(self, other: Class) -> Integer:
        return self.sm_greater_than(other)

    def __ge__(self, other: Class) -> Integer:
        return run_with_backup(
            self.sm_greater_than_or_equal,
            lambda x: Int(self.sm_greater_than(x) or self.sm_equals(x)),
            other,
        )

    @property
    def id(self) -> String:
        return String(f"{id(self):x}")

    @property
    def type(self) -> Type:
        return Type(type(self))

    @property
    def parent(self) -> Array | Type:
        parents = type(self).__bases__
        if len(parents) == 1:
            return Type(parents[0])
        return Array(map(Type, parents))

    def sm_create(self, *args: Any):
        raise NotDefinedError(self, "create")

    def sm_to_bit(self) -> Integer:
        raise NotDefinedError(self, "to_bit")

    def sm_to_string(self) -> String:
        return String(f"<{get_callable_name(type(self))}@{id(self):x}>")

    def sm_special(self) -> Any:
        raise NotDefinedError(self, "special")

    def sm_has(self, element: Any) -> Integer:
        raise NotDefinedError(self, "has")

    def sm_iterate(self) -> Array:
        raise NotDefinedError(self, "iterate")

    def sm_call(self, *args: Any) -> Any:
        raise NotDefinedError(self, "call")

    def sm_hash(self) -> Integer:
        raise NotDefinedError(self, "hash")

    def sm_subtract(self, other: Class) -> Class:
        raise NotDefinedError(self, "subtract")

    def sm_subtract_assign(self, other: Class) -> Class:
        raise NotDefinedError(self, "subtract_assign")

    def sm_add(self, other: Class) -> Class:
        raise NotDefinedError(self, "add")

    def sm_add_assign(self, other: Class) -> Class:
        raise NotDefinedError(self, "add_assign")

    def sm_multiply(self, other: Class) -> Class:
        raise NotDefinedError(self, "multiply")

    def sm_multiply_assign(self, other: Class) -> Class:
        raise NotDefinedError(self, "multiply_assign")

    def sm_divide(self, other: Class) -> Class:
        raise NotDefinedError(self, "divide")

    def sm_divide_assign(self, other: Class) -> Class:
        raise NotDefinedError(self, "divide_assign")

    def sm_mod(self, other: Class) -> Class:
        raise NotDefinedError(self, "mod")

    def sm_mod_assign(self, other: Class) -> Class:
        raise NotDefinedError(self, "mod_assign")

    def sm_power(self, other: Class) -> Class:
        raise NotDefinedError(self, "power")

    def sm_power_assign(self, other: Class) -> Class:
        raise NotDefinedError(self, "power_assign")

    def sm_and(self, other: Class) -> Class:
        raise NotDefinedError(self, "and")

    def sm_and_assign(self, other: Class) -> Class:
        raise NotDefinedError(self, "and_assign")

    def sm_or(self, other: Class) -> Class:
        raise NotDefinedError(self, "or")

    def sm_or_assign(self, other: Class) -> Class:
        raise NotDefinedError(self, "or_assign")

    def sm_xor(self, other: Class) -> Class:
        raise NotDefinedError(self, "xor")

    def sm_xor_assign(self, other: Class) -> Class:
        raise NotDefinedError(self, "xor_assign")

    def sm_negative(self) -> Class:
        raise NotDefinedError(self, "negative")

    def sm_positive(self) -> Class:
        raise NotDefinedError(self, "positive")

    def sm_not(self) -> Class:
        raise NotDefinedError(self, "not")

    def sm_get_item(self, index: Integer | Slice) -> Any:
        raise NotDefinedError(self, "get_item")

    def sm_set_item(self, index: Integer | Slice, value: Any):
        raise NotDefinedError(self, "set_item")

    def sm_equals(self, other: Class) -> Integer:
        raise NotDefinedError(self, "equals")

    def sm_not_equals(self, other: Class) -> Integer:
        raise NotDefinedError(self, "not_equals")

    def sm_less_than(self, other: Class) -> Integer:
        raise NotDefinedError(self, "less_than")

    def sm_less_than_or_equal(self, other: Class) -> Integer:
        raise NotDefinedError(self, "less_than_or_equal")

    def sm_greater_than(self, other: Class) -> Integer:
        raise NotDefinedError(self, "greater_than")

    def sm_greater_than_or_equal(self, other: Class) -> Integer:
        raise NotDefinedError(self, "greater_than_or_equal")

    def sm_cast(self):
        raise NotDefinedError(self, "cast")

    def sm_random(self):
        raise NotDefinedError(self, "random")


class Type(Class):
    def sm_create(self, type_: type):
        self.value = type_

    def sm_equals(self, other: Type) -> Integer:
        return Int(self.value == other.value)

    def sm_not_equals(self, other: Type) -> Integer:
        return Int(self.value != other.value)

    def sm_to_string(self) -> String:
        if self.value is FunctionType:
            return String("Function")
        return String(get_callable_name(self.value))

    def sm_to_bit(self) -> Integer:
        return Int(1)

    def sm_call(self, *args) -> Class:
        if self.value is FunctionType:
            raise SamariumTypeError("cannot instantiate a function")
        if self.value is Module:
            raise SamariumTypeError("cannot instantiate a module")
        return self.value(*args)


class Null(Class):
    def sm_create(self):
        self.value = None

    def sm_to_string(self) -> String:
        return String("null")

    def sm_hash(self) -> Integer:
        return Int(hash(self.value))

    def sm_to_bit(self) -> Integer:
        return Int(0)

    def sm_equals(self, other: Null) -> Integer:
        return Int(type(other) is Null)

    def sm_not_equals(self, other: Null) -> Integer:
        return Int(type(other) is not Null)


null = Null()


class Slice(Class):
    __slots__ = ("start", "stop", "step", "tup", "value", "range")

    def sm_create(self, start: Any = null, stop: Any = null, step: Any = null):
        if step.value == 0:
            raise SamariumValueError("step cannot be zero")
        self.start = start
        self.stop = stop
        self.step = step
        self.tup = start.value, stop.value, step.value
        self.range = range(
            self.tup[0] or 0,
            I64_MAX if self.tup[1] is None else self.tup[1],
            self.tup[2] or 1,
        )
        self.value = slice(*self.tup)

    def sm_iterate(self) -> Iterator:
        return Iterator(map(Int, self.range))

    def sm_random(self) -> Integer:
        if self.stop is None:
            raise SamariumValueError(
                "cannot generate a random value for slice with null stop"
            )
        return Int(choice(self.range))

    def sm_special(self) -> Integer:
        return Int(len(self.range))

    def sm_has(self, index: Integer) -> Integer:
        return Int(index.value in self.range)

    def is_empty(self) -> bool:
        return self.start == self.stop == self.step == null

    def sm_get_item(self, index: Integer) -> Integer:
        return Int(self.range[index.value])

    def sm_to_string(self) -> String:
        start, stop, step = self.start, self.stop, self.step
        if start is stop is step is null:
            return String("<<>>")
        string = ""
        if start is not null:
            string += get_repr(start)
            if stop is step is null:
                string += ".."
        if stop is not null:
            string += f"..{get_repr(stop)}"
        if step is not null:
            if stop is null:
                string += ".."
            string += f"..{get_repr(step)}"
        return String(f"<<{string}>>")

    def sm_equals(self, other: Slice) -> Integer:
        return Int(self.tup == other.tup)

    def sm_not_equals(self, other: Slice) -> Integer:
        return Int(self.tup != other.tup)


class String(Class):
    def __str__(self) -> str:
        return self.value

    def sm_hash(self) -> Integer:
        return Int(hash(self.value))

    def sm_cast(self) -> Integer:
        if len(self.value) != 1:
            raise SamariumTypeError(f"cannot cast a string of length {len(self.value)}")
        return Int(ord(self.value))

    def sm_create(self, value: Any = ""):
        self.value = str(value)

    def sm_has(self, element: String) -> Integer:
        return Int(element.value in self.value)

    def sm_iterate(self) -> Iterator:
        return Iterator(map(String, self.value))

    def sm_random(self) -> String:
        return String(choice(self.value))

    def sm_special(self) -> Integer:
        return Int(len(self.value))

    def sm_to_bit(self) -> Integer:
        return Int(self.value != "")

    def sm_to_string(self) -> String:
        return self

    def sm_add(self, other: String) -> String:
        return String(self.value + other.value)

    def sm_add_assign(self, other: String) -> String:
        self = self.sm_add(other)
        return self

    def sm_multiply(self, times: Integer) -> String:
        return String(self.value * times.value)

    def sm_multiply_assign(self, times: Integer) -> String:
        self = self.sm_multiply(times)
        return self

    def sm_equals(self, other: String) -> Integer:
        return Int(self.value == other.value)

    def sm_not_equals(self, other: String) -> Integer:
        return Int(self.value != other.value)

    def sm_greater_than(self, other: String) -> Integer:
        return Int(self.value > other.value)

    def sm_less_than(self, other: String) -> Integer:
        return Int(self.value < other.value)

    def sm_greater_than_or_equal(self, other: String) -> Integer:
        return Int(self.value >= other.value)

    def sm_less_than_or_equal(self, other: String) -> Integer:
        return Int(self.value <= other.value)

    def sm_get_item(self, index: Integer | Slice) -> String:
        return String(self.value[index.value])

    def sm_set_item(self, index: Integer | Slice, value: String):
        string = [*self.value]
        string[index.value] = value.value
        self.value = "".join(string)


class Integer(Class):
    def __int__(self) -> int:
        return self.value

    def sm_cast(self) -> String:
        return String(chr(self.value))

    def sm_hash(self) -> Integer:
        return Int(hash(self.value))

    def sm_create(self, value: Any = None):
        if hasattr(value, "value"):
            value = value.value
        if isinstance(value, (int, bool, float)):
            self.value = int(value)
        elif value is None:
            self.value = 0
        elif isinstance(value, str):
            self.value = parse_integer(value)
        else:
            raise SamariumTypeError(
                f"cannot cast {get_callable_name(type(value))} to Integer"
            )

    def sm_random(self) -> Integer:
        v = self.value
        if not v:
            return self
        elif v > 0:
            return Int(randbelow(v))
        else:
            return Int(-randbelow(v) - 1)

    def sm_to_bit(self) -> Integer:
        return Int(self.value != 0)

    def sm_to_string(self) -> String:
        return String(str(self.value))

    def sm_add(self, other: Integer) -> Integer:
        return Int(self.value + other.value)

    def sm_add_assign(self, other: Integer) -> Integer:
        self = self.sm_add(other)
        return self

    def sm_subtract(self, other: Integer) -> Integer:
        return Int(self.value - other.value)

    def sm_subtract_assign(self, other: Integer) -> Integer:
        self = self.sm_subtract(other)
        return self

    def sm_multiply(self, other: Integer) -> Integer:
        return Int(self.value * other.value)

    def sm_multiply_assign(self, other: Integer) -> Integer:
        self = self.sm_multiply(other)
        return self

    def sm_divide(self, other: Integer) -> Integer:
        return Int(self.value // other.value)

    def sm_divide_assign(self, other: Integer) -> Integer:
        self = self.sm_divide(other)
        return self

    def sm_mod(self, other: Integer) -> Integer:
        return Int(self.value % other.value)

    def sm_mod_assign(self, other: Integer) -> Integer:
        self = self.sm_mod(other)
        return self

    def sm_power(self, other: Integer) -> Integer:
        return Int(self.value ** other.value)

    def sm_power_assign(self, other: Integer) -> Integer:
        self = self.sm_power(other)
        return self

    def sm_and(self, other: Integer) -> Integer:
        return Int(self.value & other.value)

    def sm_and_assign(self, other: Integer) -> Integer:
        self = self.sm_and(other)
        return self

    def sm_or(self, other: Integer) -> Integer:
        return Int(self.value | other.value)

    def sm_or_assign(self, other: Integer) -> Integer:
        self = self.sm_or(other)
        return self

    def sm_xor(self, other: Integer) -> Integer:
        return Int(self.value ^ other.value)

    def sm_xor_assign(self, other: Integer) -> Integer:
        self = self.sm_xor(other)
        return self

    def sm_not(self) -> Integer:
        return Int(~self.value)

    def sm_negative(self) -> Integer:
        return Int(-self.value)

    def sm_positive(self) -> Integer:
        return Int(+self.value)

    def sm_equals(self, other: Integer) -> Integer:
        return Int(self.value == other.value)

    def sm_not_equals(self, other: Integer) -> Integer:
        return Int(self.value != other.value)

    def sm_greater_than(self, other: Integer) -> Integer:
        return Int(self.value > other.value)

    def sm_less_than(self, other: Integer) -> Integer:
        return Int(self.value < other.value)

    def sm_greater_than_or_equal(self, other: Integer) -> Integer:
        return Int(self.value >= other.value)

    def sm_less_than_or_equal(self, other: Integer) -> Integer:
        return Int(self.value <= other.value)

    def sm_special(self) -> String:
        return String(f"{self.value:b}")


Int = lru_cache(1024)(Integer)


class Table(Class):
    def sm_create(self, value: Any = None):
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
            raise SamariumTypeError(
                f"cannot cast {get_callable_name(type(value))} to Table"
            )

    def sm_special(self) -> Array:
        return Array(self.value.values())

    def sm_to_string(self) -> String:
        return String(
            "{{"
            + ", ".join(
                f"{get_repr(k)} -> {get_repr(v)}" for k, v in self.value.items()
            )
            + "}}"
        )

    def sm_to_bit(self) -> Integer:
        return Int(self.value != {})

    def sm_get_item(self, key: Any) -> Any:
        try:
            return self.value[key]
        except KeyError:
            raise SamariumValueError(f"key not found: {key}")

    def sm_set_item(self, key: Any, value: Any):
        self.value[key] = value

    def sm_iterate(self) -> Iterator:
        return Iterator(self.value.keys())

    def sm_random(self) -> Any:
        if not self.value:
            raise SamariumValueError("table is empty")
        return choice([*self.value.keys()])

    def sm_has(self, element: Any) -> Integer:
        return Int(element in self.value)

    def sm_equals(self, other: Table) -> Integer:
        return Int(self.value == other.value)

    def sm_not_equals(self, other: Table) -> Integer:
        return Int(self.value == other.value)

    def sm_add(self, other: Table) -> Table:
        return Table(self.value | other.value)

    def sm_add_assign(self, other: Table) -> Table:
        self.value.update(other.value)
        return self

    def sm_subtract(self, other: Class) -> Table:
        c = self.value.copy()
        try:
            del c[other]
        except KeyError:
            raise SamariumValueError(f"key not found: {other}")
        return Table(c)

    def sm_subtract_assign(self, other: Class) -> Table:
        try:
            del self.value[other]
        except KeyError:
            raise SamariumValueError(f"key not found: {other}")
        return self


class Array(Class):
    def sm_create(self, value: Any = None):
        if value is None:
            self.value = []
        elif isinstance(value, Array):
            self.value = value.value.copy()
        elif isinstance(value, String):
            self.value = Array(map(String, value.value)).value
        elif isinstance(value, Table):
            self.value = Array(map(Array, value.value.items())).value
        elif isinstance(value, Iterator):
            self.value = Array(list(value.value)).value
        elif isinstance(value, Slice) and value.sm_special() is null:
            raise SamariumTypeError("cannot convert an infinite slice to Array")
        elif isinstance(value, Iterable):
            self.value = [*map(verify_type, value)]
        else:
            raise SamariumTypeError(
                f"cannot cast {get_callable_name(type(value))} to Array"
            )

    def sm_special(self) -> Integer:
        return Int(len(self.value))

    def sm_to_string(self) -> String:
        return String(f"[{', '.join(map(get_repr, self.value))}]")

    def sm_to_bit(self) -> Integer:
        return Int(self.value != [])

    def __iter__(self) -> Iter:
        yield from self.value

    def sm_iterate(self) -> Iterator:
        return Iterator(self)

    def sm_random(self) -> Any:
        if not self.value:
            raise SamariumValueError("array is empty")
        return choice(self.value)

    def sm_has(self, element: Any) -> Integer:
        return Int(element in self.value)

    def sm_equals(self, other: Array) -> Integer:
        return Int(self.value == other.value)

    def sm_not_equals(self, other: Array) -> Integer:
        return Int(self.value != other.value)

    def sm_greater_than(self, other: Array) -> Integer:
        return Int(cmp(self.value, other.value) == 1)

    def sm_less_than(self, other: Array) -> Integer:
        return Int(cmp(self.value, other.value) == -1)

    def sm_greater_than_or_equal(self, other: Array) -> Integer:
        return Int(cmp(self.value, other.value) != -1)

    def sm_less_than_or_equal(self, other: Array) -> Integer:
        return Int(cmp(self.value, other.value) != 1)

    def sm_get_item(self, index: Integer | Slice) -> Any:
        if isinstance(index, Integer):
            return self.value[index.value]
        return Array(self.value[index.value])

    def sm_set_item(self, index: Integer | Slice, value: Any):
        self.value[index.value] = value

    def sm_add(self, other: Array) -> Array:
        return Array(self.value + other.value)

    def sm_add_assign(self, other: Array) -> Array:
        self.value += other.value
        return self

    def sm_subtract(self, other: Array | Integer) -> Array:
        new_array = self.value.copy()
        if isinstance(other, Array):
            for i in other:
                new_array.remove(i)
        elif isinstance(other, Integer):
            new_array.pop(other.value)
        else:
            raise SamariumTypeError(type(other).__name__)
        return Array(new_array)

    def sm_subtract_assign(self, other: Array | Integer) -> Array:
        if isinstance(other, Array):
            for i in other:
                self.value.remove(i)
        elif isinstance(other, Integer):
            self.value.pop(other.value)
        else:
            raise SamariumTypeError(type(other).__name__)
        return self

    def sm_multiply(self, other: Integer) -> Array:
        return Array(self.value * other.value)

    def sm_multiply_assign(self, other: Integer) -> Array:
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
        path: String | File | Integer,
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

    def sm_create(self, file: IO, mode: str, path: str, binary: bool):
        self.binary = binary
        self.mode = mode
        self.path = path
        self.value = file

    def sm_to_string(self) -> String:
        return String(f"File(path:{self.path}, mode:{self.mode})")

    def sm_not(self):
        self.value.close()
        return null

    def sm_get_item(self, index: Integer | Slice) -> Array | String | Integer | Null:
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


class Enum_(Class):
    __slots__ = ("name", "members")

    def sm_create(self, globals: dict[str, Any], *values_: str) -> None:
        if any(isinstance(i, Class) for i in values_):
            raise SamariumTypeError("enums cannot be constructed from Type")
        name, *values = values_
        self.name = name.removeprefix("sm_")
        self.members: dict[str, Class] = {}

        # Empty enum case
        if len(values) == 1 and not values[0]:
            raise SamariumValueError("enums must have at least 1 member")

        i = 0
        for v in values:
            if not v:
                continue
            eqs = v.count("=")
            if eqs >= 2:
                raise SamariumSyntaxError("invalid expression")
            name, value = v.split("=") if eqs == 1 else (v, "")
            if not name.isidentifier():
                raise SamariumValueError("enum members must be identifiers")
            if eqs == 1:
                self.members[name] = eval(value, globals)
            else:
                self.members[v] = Int(i)
                i += 1

    def sm_to_string(self) -> String:
        return String(f"Enum({self.name})")

    def __getattr__(self, name: str) -> Class:
        try:
            return self.members[name]
        except KeyError:
            raise AttributeError(f"'{self.name}''{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("sm_"):
            raise SamariumTypeError("enum members cannot be modified")
        object.__setattr__(self, name, value)


class Iterator(Class):
    __slots__ = ("value", "length")

    def sm_create(self, value: Class) -> None:
        if not isinstance(value, Iterable):
            raise SamariumTypeError("cannot create an Iterator from a non-iterable")
        self.value = iter(value)
        try:
            self.length = Int(len(value.value))
        except (TypeError, AttributeError):
            self.length = null

    def __iter__(self) -> Iter:
        return self.value

    def __next__(self) -> Class:
        return next(self.value)

    def sm_cast(self) -> Integer | Null:
        return self.length

    def sm_iterate(self) -> Iterator:
        return self

    def sm_special(self) -> Class:
        return next(self)


def class_attributes(cls):
    cls.argc = Int(len(signature(cls.sm_create).parameters))
    cls.type = Type(Type)
    parents = cls.__bases__
    cls.parent = Type(parents[0]) if len(parents) == 1 else Array(map(Type, parents))
    return cls


def cmp(arr1: list[Any], arr2: list[Any]) -> int:
    for a, b in zip(arr1, arr2):
        if a == b:
            continue
        return 1 if a > b else -1
    len1 = len(arr1)
    len2 = len(arr2)
    if len1 != len2:
        return 1 if len1 > len2 else -1
    return 0


def get_repr(obj: Class | Callable | Module) -> str:
    if isinstance(obj, String):
        return f'"{obj}"'
    return str(obj.sm_to_string())


def mkslice(start: Any = MISSING, stop: Any = MISSING, step: Any = MISSING) -> Class:
    if stop is step is MISSING:
        if start is None:
            return Slice(null, null, null)
        return start
    missing_none = {MISSING, None}
    start = null if start in missing_none else start
    stop = null if stop in missing_none else stop
    step = null if step in missing_none else step
    return Slice(start, stop, step)


def t(obj: Any = None) -> Any:
    return obj


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
        return Iterator(obj)
    else:
        raise SamariumTypeError(f"unknown type: {type(obj).__name__}")


@contextmanager
def modify(func: Callable, args: list[Any], argc: int):
    flag = func.__code__.co_flags
    if flag & 4 == 0:
        yield func, args
        return
    x = argc - 1
    args = [*args[:x], Array(args[x:])]
    func.__code__ = func.__code__.replace(co_flags=flag - 4, co_argcount=argc)
    args *= argc > 0
    yield func, args
    func.__code__ = func.__code__.replace(co_flags=flag, co_argcount=argc - 1)


MISSING_ARGS_PATTERN = compile(
    r"\w+\(\) takes exactly one argument \(0 given\)"
    r"|\w+\(\) missing (\d+) required positional argument"
)
TOO_MANY_ARGS_PATTERN = compile(
    r"\w+\(\) takes (\d+) positional arguments? but (\d+) (?:was|were) given"
)


def function(func: Callable):
    @wraps(func)
    def wrapper(*args):
        args = [*map(verify_type, args)]
        with modify(func, args, argc) as (f, args):
            try:
                result = verify_type(f(*args))
            except TypeError as e:
                errmsg = str(e)
                if "missing 1 required positional argument: 'self'" in errmsg:
                    raise SamariumTypeError("missing instance")
                missing_args = MISSING_ARGS_PATTERN.search(errmsg)
                if missing_args:
                    given = argc - (int(missing_args.group(1)) or 1)
                    raise SamariumTypeError(f"not enough arguments ({given}/{argc})")
                too_many_args = TOO_MANY_ARGS_PATTERN.search(errmsg)
                if too_many_args:
                    raise SamariumTypeError(
                        f"too many arguments ({too_many_args.group(2)}/{argc})"
                    )
                raise e
        if isinstance(result, (Class, Callable, Module)):
            return result
        raise SamariumTypeError(f"invalid return type: {type(result).__name__}")

    argc = len(signature(func).parameters)

    wrapper.sm_to_string = lambda: String(get_callable_name(func))
    wrapper.sm_special = lambda: Int(argc)
    wrapper.argc = Int(argc)
    wrapper.parent = Type(Class)
    wrapper.type = Type(FunctionType)

    return wrapper
