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
    return str(obj.sm_toString())


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
                missing_args = MISSING_ARGS_PATTERN.search(errmsg)
                if missing_args:
                    raise SamariumTypeError(
                        f"not enough arguments ({argc - (int(missing_args.group(1)) or 1)}/{argc})"
                    )
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

    wrapper.sm_toString = lambda: String(get_callable_name(func))
    wrapper.sm_special = lambda: Int(argc)
    wrapper.argc = argc
    wrapper.parent = Type(Class)
    wrapper.type = Type(FunctionType)

    return wrapper


class Class:
    __slots__ = ("value",)

    def __init__(self, *args: Any):
        with suppress(NotDefinedError):
            self.sm_create(*args)

    def __bool__(self) -> bool:
        return bool(self.sm_toBit().value)

    def __str__(self) -> str:
        return str(self.sm_toString().value)

    def __iter__(self) -> Iterator:
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
        return self.sm_subtractAssign(other)

    def __add__(self, other: Class) -> Class:
        return self.sm_add(other)

    def __iadd__(self, other: Class) -> Class:
        return self.sm_addAssign(other)

    def __mul__(self, other: Class) -> Class:
        return self.sm_multiply(other)

    def __imul__(self, other: Class) -> Class:
        return self.sm_multiplyAssign(other)

    def __floordiv__(self, other: Class) -> Class:
        return self.sm_divide(other)

    def __ifloordiv__(self, other: Class) -> Class:
        return self.sm_divideAssign(other)

    def __mod__(self, other: Class) -> Class:
        return self.sm_mod(other)

    def __imod__(self, other: Class) -> Class:
        return self.sm_modAssign(other)

    def __pow__(self, other: Class) -> Class:
        return self.sm_power(other)

    def __ipow__(self, other: Class) -> Class:
        return self.sm_powerAssign(other)

    def __and__(self, other: Class) -> Class:
        return self.sm_and(other)

    def __iand__(self, other: Class) -> Class:
        return self.sm_andAssign(other)

    def __or__(self, other: Class) -> Class:
        return self.sm_or(other)

    def __ior__(self, other: Class) -> Class:
        return self.sm_orAssign(other)

    def __xor__(self, other: Class) -> Class:
        return self.sm_xor(other)

    def __ixor__(self, other: Class) -> Class:
        return self.sm_xorAssign(other)

    def __neg__(self) -> Class:
        return self.sm_negative()

    def __pos__(self) -> Class:
        return self.sm_positive()

    def __invert__(self) -> Class:
        return self.sm_not()

    def __getitem__(self, index: Integer | Slice) -> Any:
        return self.sm_getItem(index)

    def __setitem__(self, index: Integer | Slice, value: Any):
        return self.sm_setItem(index, value)

    def __eq__(self, other: Class) -> Integer:
        return self.sm_equals(other)

    def __ne__(self, other: Class) -> Integer:
        return run_with_backup(
            self.sm_notEquals, lambda x: Int(not self.sm_equals(x)), other
        )

    def __lt__(self, other: Class) -> Integer:
        return run_with_backup(
            self.sm_lessThan,
            lambda x: Int(not (self.sm_greaterThan(x) or self.sm_equals(x))),
            other,
        )

    def __le__(self, other: Class) -> Integer:
        return run_with_backup(
            self.sm_lessThanOrEqual, lambda x: Int(not self.sm_greaterThan(x)), other
        )

    def __gt__(self, other: Class) -> Integer:
        return self.sm_greaterThan(other)

    def __ge__(self, other: Class) -> Integer:
        return run_with_backup(
            self.sm_greaterThanOrEqual,
            lambda x: Int(self.sm_greaterThan(x) or self.sm_equals(x)),
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

    def sm_create(self, *args: Any, **kwargs: Any):
        raise NotDefinedError(self, "create")

    def sm_toBit(self) -> Integer:
        raise NotDefinedError(self, "toBit")

    def sm_toString(self) -> String:
        raise NotDefinedError(self, "toString")

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

    def sm_subtractAssign(self, other: Class) -> Class:
        raise NotDefinedError(self, "subtractAssign")

    def sm_add(self, other: Class) -> Class:
        raise NotDefinedError(self, "add")

    def sm_addAssign(self, other: Class) -> Class:
        raise NotDefinedError(self, "addAssign")

    def sm_multiply(self, other: Class) -> Class:
        raise NotDefinedError(self, "multiply")

    def sm_multiplyAssign(self, other: Class) -> Class:
        raise NotDefinedError(self, "multiplyAssign")

    def sm_divide(self, other: Class) -> Class:
        raise NotDefinedError(self, "divide")

    def sm_divideAssign(self, other: Class) -> Class:
        raise NotDefinedError(self, "divideAssign")

    def sm_mod(self, other: Class) -> Class:
        raise NotDefinedError(self, "mod")

    def sm_modAssign(self, other: Class) -> Class:
        raise NotDefinedError(self, "modAssign")

    def sm_power(self, other: Class) -> Class:
        raise NotDefinedError(self, "power")

    def sm_powerAssign(self, other: Class) -> Class:
        raise NotDefinedError(self, "powerAssign")

    def sm_and(self, other: Class) -> Class:
        raise NotDefinedError(self, "and")

    def sm_andAssign(self, other: Class) -> Class:
        raise NotDefinedError(self, "andAssign")

    def sm_or(self, other: Class) -> Class:
        raise NotDefinedError(self, "or")

    def sm_orAssign(self, other: Class) -> Class:
        raise NotDefinedError(self, "orAssign")

    def sm_xor(self, other: Class) -> Class:
        raise NotDefinedError(self, "xor")

    def sm_xorAssign(self, other: Class) -> Class:
        raise NotDefinedError(self, "xorAssign")

    def sm_negative(self) -> Class:
        raise NotDefinedError(self, "negative")

    def sm_positive(self) -> Class:
        raise NotDefinedError(self, "positive")

    def sm_not(self) -> Class:
        raise NotDefinedError(self, "not")

    def sm_getItem(self, index: Integer | Slice) -> Any:
        raise NotDefinedError(self, "getItem")

    def sm_setItem(self, index: Integer | Slice, value: Any):
        raise NotDefinedError(self, "setItem")

    def sm_equals(self, other: Class) -> Integer:
        raise NotDefinedError(self, "equals")

    def sm_notEquals(self, other: Class) -> Integer:
        raise NotDefinedError(self, "notEquals")

    def sm_lessThan(self, other: Class) -> Integer:
        raise NotDefinedError(self, "lessThan")

    def sm_lessThanOrEqual(self, other: Class) -> Integer:
        raise NotDefinedError(self, "lessThanOrEqual")

    def sm_greaterThan(self, other: Class) -> Integer:
        raise NotDefinedError(self, "greaterThan")

    def sm_greaterThanOrEqual(self, other: Class) -> Integer:
        raise NotDefinedError(self, "greaterThanOrEqual")

    def sm_cast(self):
        raise NotDefinedError(self, "cast")

    def sm_random(self):
        raise NotDefinedError(self, "random")


class Type(Class):
    def sm_create(self, type_: type):
        self.value = type_

    def sm_equals(self, other: Type) -> Integer:
        return Int(self.value == other.value)

    def sm_notEquals(self, other: Type) -> Integer:
        return Int(self.value != other.value)

    def sm_toString(self) -> String:
        if self.value is FunctionType:
            return String("Function")
        return String(get_callable_name(self.value))

    def sm_toBit(self) -> Integer:
        return Int(1)

    def sm_call(self, *args) -> Class:
        if self.value is FunctionType:
            raise SamariumTypeError("cannot instantiate a function")
        if self.value is Module:
            raise SamariumTypeError("cannot instantiate a module")
        return self.value(*args)


class Slice(Class):
    __slots__ = ("start", "stop", "step", "tup", "value")

    def sm_create(self, start: Any, stop: Any, step: Any):
        self.start = start
        self.stop = stop
        self.step = step
        self.tup = start.value, stop.value, step.value
        self.value = slice(*self.tup)

    def sm_random(self) -> Integer:
        if self.stop is None:
            raise SamariumValueError(
                "cannot generate a random value for slice with null stop"
            )
        tup = self.tup[0] or 0, self.tup[1], self.tup[2] or 1
        range_ = range(*tup)
        return Int(choice(range_))

    def is_empty(self) -> bool:
        return self.start == self.stop == self.step == null

    def sm_toString(self) -> String:
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
            string += f"**{get_repr(step)}"
        return String(f"<<{string}>>")

    def sm_equals(self, other: Slice) -> Integer:
        return Int(self.tup == other.tup)

    def sm_notEquals(self, other: Slice) -> Integer:
        return Int(self.tup != other.tup)


class Null(Class):
    def sm_create(self):
        self.value = None

    def sm_toString(self) -> String:
        return String("null")

    def sm_hash(self) -> Integer:
        return Int(hash(self.value))

    def sm_toBit(self) -> Integer:
        return Int(0)

    def sm_equals(self, other: Null) -> Integer:
        return Int(type(other) is Null)

    def sm_notEquals(self, other: Null) -> Integer:
        return Int(type(other) is not Null)


null = Null()


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

    def sm_iterate(self) -> Array:
        return Array(map(String, self.value))

    def sm_random(self) -> String:
        return String(choice(self.value))

    def sm_special(self) -> Integer:
        return Int(len(self.value))

    def sm_toBit(self) -> Integer:
        return Int(self.value != "")

    def sm_toString(self) -> String:
        return self

    def sm_add(self, other: String) -> String:
        return String(self.value + other.value)

    def sm_addAssign(self, other: String) -> String:
        self = self.sm_add(other)
        return self

    def sm_multiply(self, times: Integer) -> String:
        return String(self.value * times.value)

    def sm_multiplyAssign(self, times: Integer) -> String:
        self = self.sm_multiply(times)
        return self

    def sm_equals(self, other: String) -> Integer:
        return Int(self.value == other.value)

    def sm_notEquals(self, other: String) -> Integer:
        return Int(self.value != other.value)

    def sm_greaterThan(self, other: String) -> Integer:
        return Int(self.value > other.value)

    def sm_lessThan(self, other: String) -> Integer:
        return Int(self.value < other.value)

    def sm_greaterThanOrEqual(self, other: String) -> Integer:
        return Int(self.value >= other.value)

    def sm_lessThanOrEqual(self, other: String) -> Integer:
        return Int(self.value <= other.value)

    def sm_getItem(self, index: Integer | Slice) -> String:
        return String(self.value[index.value])

    def sm_setItem(self, index: Integer | Slice, value: String):
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

    def sm_random(self) -> Integer:
        v = self.value
        if not v:
            return self
        elif v > 0:
            return Int(randbelow(v))
        else:
            return Int(-randbelow(v) - 1)

    def sm_toBit(self) -> Integer:
        return Int(self.value != 0)

    def sm_toString(self) -> String:
        return String(str(self.value))

    def sm_add(self, other: Integer) -> Integer:
        return Int(self.value + other.value)

    def sm_addAssign(self, other: Integer) -> Integer:
        self = self.sm_add(other)
        return self

    def sm_subtract(self, other: Integer) -> Integer:
        return Int(self.value - other.value)

    def sm_subtractAssign(self, other: Integer) -> Integer:
        self = self.sm_subtract(other)
        return self

    def sm_multiply(self, other: Integer) -> Integer:
        return Int(self.value * other.value)

    def sm_multiplyAssign(self, other: Integer) -> Integer:
        self = self.sm_multiply(other)
        return self

    def sm_divide(self, other: Integer) -> Integer:
        return Int(self.value // other.value)

    def sm_divideAssign(self, other: Integer) -> Integer:
        self = self.sm_divide(other)
        return self

    def sm_mod(self, other: Integer) -> Integer:
        return Int(self.value % other.value)

    def sm_modAssign(self, other: Integer) -> Integer:
        self = self.sm_mod(other)
        return self

    def sm_power(self, other: Integer) -> Integer:
        return Int(self.value ** other.value)

    def sm_powerAssign(self, other: Integer) -> Integer:
        self = self.sm_power(other)
        return self

    def sm_and(self, other: Integer) -> Integer:
        return Int(self.value & other.value)

    def sm_andAssign(self, other: Integer) -> Integer:
        self = self.sm_and(other)
        return self

    def sm_or(self, other: Integer) -> Integer:
        return Int(self.value | other.value)

    def sm_orAssign(self, other: Integer) -> Integer:
        self = self.sm_or(other)
        return self

    def sm_xor(self, other: Integer) -> Integer:
        return Int(self.value ^ other.value)

    def sm_xorAssign(self, other: Integer) -> Integer:
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

    def sm_notEquals(self, other: Integer) -> Integer:
        return Int(self.value != other.value)

    def sm_greaterThan(self, other: Integer) -> Integer:
        return Int(self.value > other.value)

    def sm_lessThan(self, other: Integer) -> Integer:
        return Int(self.value < other.value)

    def sm_greaterThanOrEqual(self, other: Integer) -> Integer:
        return Int(self.value >= other.value)

    def sm_lessThanOrEqual(self, other: Integer) -> Integer:
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
            raise SamariumTypeError(f"cannot cast {type(value).__name__} to Table")

    def sm_special(self) -> Array:
        return Array(self.value.values())

    def sm_toString(self) -> String:
        return String(
            "{{"
            + ", ".join(
                f"{get_repr(k)} -> {get_repr(v)}" for k, v in self.value.items()
            )
            + "}}"
        )

    def sm_toBit(self) -> Integer:
        return Int(self.value != {})

    def sm_getItem(self, key: Any) -> Any:
        try:
            return self.value[key]
        except KeyError:
            raise SamariumValueError(f"key not found: {key}")

    def sm_setItem(self, key: Any, value: Any):
        self.value[key] = value

    def sm_iterate(self) -> Array:
        return Array(self.value.keys())

    def sm_random(self) -> Any:
        if not self.value:
            raise SamariumValueError("table is empty")
        return choice([*self.value.keys()])

    def sm_has(self, element: Any) -> Integer:
        return Int(element in self.value)

    def sm_equals(self, other: Table) -> Integer:
        return Int(self.value == other.value)

    def sm_notEquals(self, other: Table) -> Integer:
        return Int(self.value == other.value)

    def sm_add(self, other: Table) -> Table:
        return Table(self.value | other.value)

    def sm_addAssign(self, other: Table) -> Table:
        self.value.update(other.value)
        return self

    def sm_subtract(self, other: Class) -> Table:
        c = self.value.copy()
        try:
            del c[other]
        except KeyError:
            raise SamariumValueError(f"key not found: {other}")
        return Table(c)

    def sm_subtractAssign(self, other: Class) -> Table:
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
        elif isinstance(value, Iterable):
            self.value = [*map(verify_type, value)]
        else:
            raise SamariumTypeError(f"cannot cast {type(value).__name__} to Array")

    def sm_special(self) -> Integer:
        return Int(len(self.value))

    def sm_toString(self) -> String:
        return String(f"[{', '.join(map(get_repr, self.value))}]")

    def sm_toBit(self) -> Integer:
        return Int(self.value != [])

    def __iter__(self) -> Iterator:
        yield from self.value

    def sm_iterate(self) -> Array:
        return self

    def sm_random(self) -> Any:
        if not self.value:
            raise SamariumValueError("array is empty")
        return choice(self.value)

    def sm_has(self, element: Any) -> Integer:
        return Int(element in self.value)

    def sm_equals(self, other: Array) -> Integer:
        return Int(self.value == other.value)

    def sm_notEquals(self, other: Array) -> Integer:
        return Int(self.value != other.value)

    def sm_greaterThan(self, other: Array) -> Integer:
        return Int(self.value > other.value)

    def sm_lessThan(self, other: Array) -> Integer:
        return Int(self.value < other.value)

    def sm_greaterThanOrEqual(self, other: Array) -> Integer:
        return Int(self.value >= other.value)

    def sm_lessThanOrEqual(self, other: Array) -> Integer:
        return Int(self.value <= other.value)

    def sm_getItem(self, index: Integer | Slice) -> Any:
        if isinstance(index, Integer):
            return self.value[index.value]
        return Array(self.value[index.value])

    def sm_setItem(self, index: Integer | Slice, value: Any):
        self.value[index.value] = value

    def sm_add(self, other: Array) -> Array:
        return Array(self.value + other.value)

    def sm_addAssign(self, other: Array) -> Array:
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

    def sm_subtractAssign(self, other: Array | Integer) -> Array:
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

    def sm_multiplyAssign(self, other: Integer) -> Array:
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

    def sm_toString(self) -> String:
        return String(f"File(path:{self.path}, mode:{self.mode})")

    def sm_not(self):
        self.value.close()
        return null

    def sm_getItem(self, index: Integer | Slice) -> Array | String | Integer | Null:
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
    def sm_create(self, globals: dict[str, Any], *values_: str):
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

    def sm_toString(self) -> String:
        return String(f"Enum({self.name})")

    def __getattr__(self, name: str) -> Class:
        try:
            return self.members[name]
        except KeyError:
            raise AttributeError(f"'{self.name}''{name}'")