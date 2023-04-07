from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from collections.abc import Iterator as PyIterator
from contextlib import suppress
from functools import lru_cache
from inspect import signature
from random import choice, randrange, uniform
from types import GeneratorType, MethodType
from typing import Any, Generic, TypeVar, cast

from ..exceptions import (
    NotDefinedError,
    SamariumSyntaxError,
    SamariumTypeError,
    SamariumValueError,
)
from ..utils import (
    ClassProperty,
    Singleton,
    get_name,
    get_type_name,
    parse_number,
    smformat,
)

T = TypeVar("T")
KT = TypeVar("KT")
VT = TypeVar("VT")

MISSING_POSARG = re.compile(r"missing (\d+) required positional argument")


def functype_repr(obj: Any) -> str:
    return (
        get_name(obj)
        if isinstance(obj, type) and issubclass(obj, UserAttrs)
        else repr(obj)
    )


def guard(operator: str, *, default: int | None = None) -> Callable[..., Any]:
    def decorator(function: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(self: Any, other: Any) -> Any:
            Ts = type(self)
            To = type(other)
            use_default = default is not None and other.val is None
            if isinstance(other, Ts):
                return function(self, other)
            if use_default:
                return function(self, Num(default))
            raise NotDefinedError(f"{Ts.__name__} {operator} {To.__name__}")

        return wrapper

    return decorator


def throw_missing(*_: Any) -> None:
    raise SamariumTypeError("missing default parameter value(s)")


class Missing:
    @classmethod
    def type(cls) -> None:
        throw_missing()

    @classmethod
    def parent(cls) -> None:
        throw_missing()

    @classmethod
    def id(cls) -> None:
        throw_missing()


METHODS = (
    "getattr add str sub mul truediv pow mod and or xor neg pos invert getitem "
    "setitem eq ne ge gt le lt contains hash call iter matmul"
)

for m in METHODS.split():
    setattr(Missing, f"__{m}__", throw_missing)

MISSING = Missing()
NEXT = object()


class Attrs:
    def __getattribute__(self, name: str) -> Any:
        attr = object.__getattribute__(self, name)
        if isinstance(attr, Function) and "self" in signature(attr.func).parameters:
            return Function(attr.func, self)
        return attr

    @classmethod
    def id(cls) -> String:
        return String(f"{id(cls):x}")

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def type(cls) -> Type:
        return Type(cls)

    parent = type


class UserAttrs(Attrs):
    def __entry__(self, *args: Any) -> None:
        ...

    def __init__(self, *args: Any) -> None:
        self.__entry__(*args)

    def __string__(self) -> String:
        return String(f"<{get_type_name(self)}@{self.id()}>")

    __string__.param_count = 1

    def __str__(self) -> str:
        string = self.__string__
        if param_count(string) != 1:
            raise SamariumTypeError(
                f"{get_type_name(self)}! should only take one argument"
            )
        if isinstance(v := string().val, str):
            return v
        raise SamariumTypeError(f"{get_type_name(self)}! returned a non-string")

    def __bit__(self) -> Number:
        raise NotDefinedError(f"? {get_type_name(self)}")

    __bit__.param_count = 1

    def __bool__(self) -> bool:
        bit = self.__bit__
        if param_count(bit) != 1:
            raise SamariumTypeError(
                f"? {get_type_name(self)} should only take one argument"
            )
        if (v := bit().val) in (0, 1):
            return bool(v)
        raise SamariumTypeError(f"? {get_type_name(self)} returned a non-bit")

    def __hash__(self) -> int:
        return cast(int, self.hash().val)

    def __special__(self) -> Any:
        raise NotDefinedError(f"{get_type_name(self)}$")

    __special__.param_count = 1

    def special(self) -> Any:
        special = self.__special__
        if param_count(special) != 1:
            raise SamariumTypeError(
                f"{get_type_name(self)}$ should only take one argument"
            )
        return special()

    def __hsh__(self) -> Number:
        raise NotDefinedError(f"{get_type_name(self)}##")

    __hsh__.param_count = 1

    def hash(self) -> Number:
        hsh = self.__hsh__
        if param_count(hsh) != 1:
            raise SamariumTypeError(
                f"{get_type_name(self)}## should only take one argument"
            )
        if isinstance(v := hsh(), Number):
            return v
        raise SamariumTypeError(f"{get_type_name(self)}## returned a non-integer")

    def __cast__(self) -> Any:
        raise NotDefinedError(f"{get_type_name(self)}%")

    __cast__.param_count = 1

    def cast(self) -> Any:
        cast = self.__cast__
        if param_count(cast) != 1:
            raise SamariumTypeError(
                f"{get_type_name(self)}% should only take one argument"
            )
        return cast()

    def __random__(self) -> Number:
        raise NotDefinedError(f"{get_type_name(self)}??")

    __random__.param_count = 1

    def random(self) -> Any:
        random = self.__random__
        if param_count(random) != 1:
            raise SamariumTypeError(
                f"{get_type_name(self)}?? should only take one argument"
            )
        return random()

    @ClassProperty
    def param_count(self) -> int:
        return len(signature(self.__init__).parameters)

    @classmethod
    def parent(cls) -> Array | Type:
        parents = cls.__bases__
        if len(parents) == 1:
            parent = parents[0]
            if parent is object:
                return Type(cls)
            if parent is UserAttrs:
                return Type(Type)
            return Type(parent)
        return Array(map(Type, parents))


class Type(Attrs):
    __slots__ = ("val",)

    def __init__(self, type_: type) -> None:
        self.val = type_

    def __eq__(self, other: Any) -> Number:
        if isinstance(other, Type):
            return Num(self.val == other.val)
        return Num(self.val == other)

    def __ne__(self, other: Any) -> Number:
        if isinstance(other, Type):
            return Num(self.val != other.val)
        return Num(self.val != other)

    def __str__(self) -> str:
        return get_name(self.val)

    __repr__ = __str__

    def __bool__(self) -> bool:
        return True

    def __hash__(self) -> int:
        return hash(self.val)

    def __call__(self, *args: Any) -> Any:
        if self.val in (Function, Module, Type):
            raise SamariumTypeError(f"cannot instantiate a {self.val.__name__.lower()}")
        return self.val(*args)


class Module(Attrs):
    __slots__ = ("name", "objects")

    def __init__(self, name: str, objects: dict[str, Any]) -> None:
        self.name = name
        self.objects = objects

    def __bool__(self) -> bool:
        return True

    def __str__(self) -> str:
        return f"Module[{self.name}]"

    __repr__ = __str__

    def __getattr__(self, key: str) -> Any:
        return self.objects[key]


class Number(Attrs):
    __slots__ = ("is_int", "val")

    def __init__(self, v: Any = None) -> None:
        self.val: int | float
        t = type(v)
        if t in (int, bool):
            self.is_int = True
            self.val = int(v)
        elif t is float:
            self.is_int = is_int = v.is_integer()
            self.val = int(v) if is_int else v
        elif t is Number:
            self.val = v.val
            self.is_int = v.is_int
        elif t is String:
            val, is_int = parse_number(v.val) if v else (0, True)
            self.val = int(val) if is_int else val
            self.is_int = is_int
        elif v in (None, NULL):
            self.val = 0
            self.is_int = True
        else:
            raise SamariumTypeError(f"cannot cast {get_name(t)} to Number")

    def __bool__(self) -> bool:
        return self.val != 0.0

    def __str__(self) -> str:
        return str(self.val)

    __repr__ = __str__

    @guard("+", default=1)
    def __add__(self, other: Any) -> Number:
        return Num(self.val + other.val)

    @guard("-", default=1)
    def __sub__(self, other: Any) -> Number:
        return Num(self.val - other.val)

    def __mul__(self, other: Any) -> String | Number:
        if isinstance(other, String):
            return other * self
        if other is NULL:
            other = Num(2)
        return Num(self.val * other.val)

    @guard("--", default=2)
    def __truediv__(self, other: Any) -> Number:
        return Num(self.val / other.val)

    @guard("+++", default=2)
    def __pow__(self, other: Any) -> Number:
        return Num(self.val**other.val)

    @guard("---", default=2)
    def __mod__(self, other: Any) -> Number:
        return Num(self.val % other.val)

    @guard("&")
    def __and__(self, other: Any) -> Number:
        if self.is_int and other.is_int:
            return Num(self.val & other.val)
        raise SamariumValueError("cannot use & with non-integer numbers")

    @guard("|")
    def __or__(self, other: Any) -> Number:
        if self.is_int and other.is_int:
            return Num(self.val | other.val)
        raise SamariumValueError("cannot use | with non-integer numbers")

    @guard("^")
    def __xor__(self, other: Any) -> Number:
        if self.is_int and other.is_int:
            return Num(self.val ^ other.val)
        raise SamariumValueError("cannot use ^ with non-integer numbers")

    def __invert__(self) -> Number:
        if self.is_int:
            return Num(~cast(int, self.val))
        raise SamariumValueError("cannot invert a non-integer number")

    def __pos__(self) -> Number:
        return self

    def __neg__(self) -> Number:
        return Num(-self.val)

    def __eq__(self, other: Any) -> Number:
        if isinstance(other, Number):
            return Num(self.val == other.val)
        return Num(0.0)

    def __ne__(self, other: Any) -> Number:
        if isinstance(other, Number):
            return Num(self.val != other.val)
        return Num(1.0)

    @guard(">", default=0)
    def __gt__(self, other: Any) -> Number:
        return Num(self.val > other.val)

    @guard(">:", default=0)
    def __ge__(self, other: Any) -> Number:
        return Num(self.val >= other.val)

    @guard("<", default=0)
    def __lt__(self, other: Any) -> Number:
        return Num(self.val < other.val)

    @guard("<:", default=0)
    def __le__(self, other: Any) -> Number:
        return Num(self.val <= other.val)

    def __hash__(self) -> float:
        return self.hash().val

    def cast(self) -> String:
        if self.is_int:
            return String(to_chr(cast(int, self.val)))
        raise SamariumValueError("cannot cast a non-integer number")

    def hash(self) -> Number:
        return Num(hash(self.val))

    def random(self) -> Number:
        if not self:
            return self
        if self.is_int:
            v = cast(int, self.val)
            r = randrange(v)
            if v > 0:
                return Num(r)
            return Num(~r)
        v = self.val
        u = uniform(0, v)
        if v > 0.0:
            return Num(u)
        return Num(-u - 1)

    def special(self) -> Number:
        return Number(int(self.val))


Num = lru_cache(1024)(Number)


class String(Attrs):
    __slots__ = ("val",)

    def __init__(self, value: Any = "") -> None:
        self.val = to_string(value)

    def __contains__(self, element: String) -> bool:
        return element.val in self.val

    def __iter__(self) -> PyIterator[String]:
        yield from map(String, self.val)

    def __bool__(self) -> bool:
        return self.val != ""

    def __str__(self) -> str:
        return self.val

    def __repr__(self) -> str:
        return f'"{repr(self.val)[1:-1]}"'

    def __add__(self, other: Any) -> String:
        if isinstance(other, String):
            return String(self.val + other.val)
        if isinstance(other, Number):
            if other.is_int:
                return String(
                    "".join(
                        chr((ord(i) + cast(int, other.val)) % 0x10FFFF)
                        for i in self.val
                    )
                )
            raise SamariumTypeError("cannot shift using non-integers")
        raise SamariumTypeError(f"String + {get_type_name(other)}")

    def __sub__(self, other: Any) -> String:
        if isinstance(other, String):
            return String(self.val.replace(other.val, "", 1))
        if isinstance(other, Number):
            return self + (-other)
        raise SamariumTypeError(f"String - {get_type_name(other)}")

    @guard("--")
    def __truediv__(self, other: Any) -> String:
        return String(self.val.replace(other.val, ""))

    def __mul__(self, other: Any) -> String:
        if other is NULL:
            other = Num(2)
        if isinstance(other, Number):
            i, d = int(other.val // 1), other.val % 1
            return String(self.val * i + self.val[: round(d * len(self.val))])
        raise NotDefinedError(f"String ++ {get_type_name(other)}")

    def __mod__(self, other: Any) -> String:
        if isinstance(other, (String, Array, Table)):
            return String(smformat(self.val, other.val))
        raise NotDefinedError(f"String --- {get_type_name(other)}")

    def __eq__(self, other: Any) -> Number:
        return Num(self.val == other.val)

    def __ne__(self, other: Any) -> Number:
        return Num(self.val != other.val)

    @guard(">")
    def __gt__(self, other: Any) -> Number:
        return Num(self.val > other.val)

    @guard(">:")
    def __ge__(self, other: Any) -> Number:
        return Num(self.val >= other.val)

    @guard("<")
    def __lt__(self, other: Any) -> Number:
        return Num(self.val < other.val)

    @guard("<:")
    def __le__(self, other: Any) -> Number:
        return Num(self.val <= other.val)

    def __getitem__(self, index: Number | Slice) -> String:
        if isinstance(index, Number):
            if not is_valid_index(self, index):
                raise SamariumTypeError(f"invalid index: {index}")
            return String(self.val[cast(int, index.val)])
        if isinstance(index, Slice):
            return String(self.val[index.val])
        raise SamariumTypeError(f"invalid index: {index}")

    def __setitem__(self, index: Number | Slice, value: String) -> None:
        if not isinstance(index, (Number, Slice)):
            raise SamariumTypeError(f"invalid index: {index}")
        if isinstance(index, Number):
            if not is_valid_index(self, index):
                raise SamariumTypeError(f"invalid index: {index}")
            i = cast(int, index.val)
        else:
            i = index.val
        string = [*self.val]
        string[i] = value.val
        self.val = "".join(string)

    def __hash__(self) -> int:
        return cast(int, self.hash().val)

    def __matmul__(self, other: Any) -> Zip:
        return Zip(self, other)

    def cast(self) -> Array | Number:
        if len(self.val) == 1:
            return Num(ord(self.val))
        return Array(Num(ord(i)) for i in self.val)

    def hash(self) -> Number:
        return Num(hash(self.val))

    def random(self) -> String:
        return String(choice(self.val))

    def special(self) -> Number:
        return Num(len(self.val))


class Array(Generic[T], Attrs):
    __slots__ = ("val",)

    def __init__(self, value: Any = None) -> None:
        self.val: list[Any]
        if value is None:
            self.val = []
        elif isinstance(value, Array):
            self.val = value.val.copy()
        elif isinstance(value, String):
            self.val = list(map(String, value.val))
        elif isinstance(value, Table):
            self.val = list(map(Array, value.val.items()))
        elif isinstance(value, Slice):
            if value.stop is NULL:
                raise SamariumValueError("cannot convert an infinite Slice to an Array")
            self.val = list(value)
        elif isinstance(value, Iterable):
            self.val = [*value]
        else:
            raise SamariumTypeError(f"cannot cast {get_type_name(value)} to an Array")

    def __str__(self) -> str:
        return "[{}]".format(", ".join(map(functype_repr, self.val)))

    __repr__ = __str__

    def __bool__(self) -> bool:
        return self.val != []

    def __iter__(self) -> PyIterator[T]:
        yield from self.val

    def __contains__(self, element: T) -> bool:
        return element in self.val

    def __eq__(self, other: Any) -> Number:
        if isinstance(other, Array):
            return Num(self.val == other.val)
        return Num(0)

    def __ne__(self, other: Any) -> Number:
        if isinstance(other, Array):
            return Num(self.val != other.val)
        return Num(1)

    @guard(">")
    def __gt__(self, other: Any) -> Number:
        return Num(self.val > other.val)

    @guard(">:")
    def __ge__(self, other: Any) -> Number:
        return Num(self.val >= other.val)

    @guard("<")
    def __lt__(self, other: Any) -> Number:
        return Num(self.val < other.val)

    @guard("<:")
    def __le__(self, other: Any) -> Number:
        return Num(self.val <= other.val)

    def __getitem__(self, index: Any) -> T | Array[T]:
        if isinstance(index, Number):
            if not is_valid_index(self, index):
                raise SamariumValueError(f"invalid index: {index}")
            return self.val[cast(int, index.val)]
        if isinstance(index, Slice):
            return Array(self.val[index.val])
        raise SamariumTypeError(f"invalid index: {index}")

    def __setitem__(self, index: Any, value: T | Array[T]) -> None:
        if not isinstance(index, (Number, Slice)):
            raise SamariumTypeError(f"invalid index: {index}")
        if isinstance(index, Number):
            if not is_valid_index(self, index):
                raise SamariumValueError(f"invalid index: {index}")
            self.val[cast(int, index.val)] = value
        else:
            self.val[index.val] = cast(Array[T], value)

    @guard("+")
    def __add__(self, other: Any) -> Array[T]:
        return Array(self.val + other.val)

    def __sub__(self, other: Any) -> Array[T]:
        new_array = self.val.copy()
        if isinstance(other, Array):
            for i in other:
                try:
                    new_array.remove(i)
                except ValueError:
                    raise SamariumValueError(f"{i!r} not in array") from None
        elif isinstance(other, Number):
            if not other.is_int:
                raise SamariumValueError(f"invalid index: {other}")
            new_array.pop(cast(int, other.val))
        elif other is NULL:
            return self.val.pop()
        else:
            raise NotDefinedError(f"Array - {get_type_name(other)}")
        return Array(new_array)

    def __neg__(self) -> Array[T]:
        new_array = []
        for i in self.val:
            if i not in new_array:
                new_array.append(i)
        return Array(new_array)

    def __mod__(self, other: Any) -> Array[T]:
        indexes = [i for i, v in enumerate(self.val) if v == other]
        new_array = self.val.copy()
        for i in indexes[1:][::-1]:
            new_array.pop(i)
        return Array(new_array)

    @guard("--")
    def __truediv__(self, other: Any) -> Array[T]:
        new_array = self.val.copy()
        for i in other.val:
            with suppress(ValueError):
                new_array.remove(i)
        return Array(new_array)

    @guard("|")
    def __or__(self, other: Any) -> Array[T]:
        new_array = self.val.copy()
        for i in other.val:
            if i not in new_array:
                new_array.append(i)
        return Array(new_array)

    @guard("&")
    def __and__(self, other: Any) -> Array[T]:
        return Array([i for i in other.val if i in self.val])

    @guard("^")
    def __xor__(self, other: Any) -> Array[T]:
        return (self | other) / (self & other)

    def __mul__(self, other: Any) -> Array[T]:
        if isinstance(other, Number):
            i, d = int(other.val // 1), other.val % 1
            return Array(self.val * i + self.val[: round(d * len(self.val))])
        raise NotDefinedError(f"Array ++ {get_type_name(other)}")

    def __matmul__(self, other: Any) -> Zip:
        return Zip(self, other)

    def cast(self) -> String:
        s = ""
        for i in self.val:
            if isinstance(i, Number) and i.is_int:
                s += to_chr(cast(int, i.val))
            else:
                raise SamariumTypeError("array contains non-integers")
        return String(s)

    def random(self) -> T:
        if not self.val:
            raise SamariumValueError("array is empty")
        return choice(self.val)

    def special(self) -> Number:
        return Num(len(self.val))


class Table(Generic[KT, VT], Attrs):
    __slots__ = ("val",)

    def __init__(self, value: Any = None) -> None:
        if value is None:
            self.val = {}
        elif isinstance(value, Table):
            self.val = value.val.copy()
        elif isinstance(value, dict):
            self.val = value
        elif isinstance(value, Array):
            arr = value.val
            if all(isinstance(i, (String, Array)) and len(i.val) == 2 for i in arr):
                table = {}
                for e in arr:
                    if isinstance(e, String):
                        k, v = map(String, e.val)
                        table[k] = v
                    else:
                        k, v = e.val
                        table[k] = v
                self.val = table
            else:
                raise SamariumValueError(
                    "not all elements of the array are of length 2"
                )
        else:
            raise SamariumTypeError(f"cannot cast {get_type_name(value)} to a Table")

    def __str__(self) -> str:
        return (
            "{{"
            + ", ".join(
                "{} -> {}".format(*map(functype_repr, i)) for i in self.val.items()
            )
            + "}}"
        )

    def __bool__(self) -> bool:
        return self.val != {}

    def __getitem__(self, key: KT) -> VT:
        try:
            return self.val[key]
        except KeyError:
            raise SamariumValueError(f"key not found: {key}") from None

    def __setitem__(self, key: KT, value: VT) -> None:
        # print(key, hash(key))
        # print(value, hash(value))
        self.val[key] = value

    def __iter__(self) -> PyIterator[KT]:
        yield from self.val.keys()

    def __contains__(self, element: Any) -> bool:
        # print("Table.__contains__", self.val, element, type(element))
        # print("hsh", hash(element))
        return element in self.val

    def __eq__(self, other: Any) -> Number:
        if isinstance(other, Table):
            return Num(self.val == other.val)
        return Num(0)

    def __ne__(self, other: Any) -> Number:
        if isinstance(other, Table):
            return Num(self.val != other.val)
        return Num(1)

    @guard("+")
    def __add__(self, other: Any) -> Table[KT, VT]:
        return Table(self.val | other.val)

    def __sub__(self, other: Any) -> Table[KT, VT]:
        c = self.val.copy()
        try:
            del c[other]
        except KeyError:
            raise SamariumValueError(f"key not found: {other}") from None
        return Table(c)

    def __matmul__(self, other: Any) -> Zip:
        return Zip(self, other)

    def random(self) -> Any:
        if not self.val:
            raise SamariumValueError("table is empty")
        return choice(list(self.val.keys()))

    def special(self) -> Array[VT]:
        return Array(self.val.values())


class Null(Singleton, Attrs):
    __slots__ = ("val",)

    def __init__(self) -> None:
        self.val = None

    def __str__(self) -> str:
        return "null"

    __repr__ = __str__

    def __bool__(self) -> bool:
        return False

    def __eq__(self, other: Any) -> bool:
        return self is other

    def __ne__(self, other: Any) -> bool:
        return self is not other

    def __hash__(self) -> int:
        return cast(int, self.hash().val)

    def hash(self) -> Number:
        return Num(hash(self.val))

    def __invert__(self) -> Number:
        return Num(-1)

    def __floordiv__(self, other: Any) -> Number:
        return Num(not other)


I64_MAX = 9223372036854775807
NULL = Null()


class Slice(Attrs):
    __slots__ = ("start", "stop", "step", "tup", "range", "val")

    def __init__(self, start: Any, stop: Any = NULL, step: Any = NULL) -> None:
        if step.val == 0:
            raise SamariumValueError("step cannot be zero")
        self.start = start
        self.stop = stop
        self.step = step
        self.tup = start.val, stop.val, step.val
        try:
            self.range = range(
                self.tup[0] or 0,
                I64_MAX if self.tup[1] is None else self.tup[1],
                self.tup[2] or 1,
            )
        except TypeError:
            raise SamariumTypeError("slice values have to be integers") from None
        self.val = slice(*self.tup)

    def __bool__(self) -> bool:
        return bool(self.range)

    def __iter__(self) -> PyIterator[Number]:
        yield from map(Num, self.range)

    def __contains__(self, value: Number) -> Number:
        return Num(value.val in self.range)

    def __getitem__(self, index: Number) -> Number:
        if not isinstance(index, Number):
            raise SamariumTypeError(f"invalid index: {index}")
        if is_valid_index(self, index):
            return Num(self.range[cast(int, index.val)])
        raise SamariumValueError(f"invalid index: {index}")

    def __str__(self) -> str:
        start, stop, step = self.tup
        if self.is_empty():
            return "<<>>"
        string = ""
        if start is not None:
            string += repr(start)
            if stop is step is None:
                string += ".."
        if stop is not None:
            string += f"..{stop!r}"
        if step is not None:
            if stop is None:
                string += ".."
            string += f"..{step!r}"
        return f"<<{string}>>"

    def __matmul__(self, other: Any) -> Zip:
        return Zip(self, other)

    __repr__ = __str__

    def __eq__(self, other: Any) -> Number:
        if isinstance(other, Slice):
            return Num(self.tup == other.tup)
        return Num(0)

    def __ne__(self, other: Any) -> Number:
        if isinstance(other, Slice):
            return Num(self.tup != other.tup)
        return Num(1)

    def __hash__(self) -> int:
        return cast(int, self.hash().val)

    def hash(self) -> Number:
        return Num(hash(self.tup))

    def random(self) -> Number:
        return Num(choice(self.range))

    def special(self) -> Number:
        return Num(len(self.range))

    def is_empty(self) -> bool:
        return self.start is self.stop is self.step is NULL


class Zip(Attrs):
    __slots__ = ("iters", "val")

    def __init__(self, *values: Any) -> None:
        if not all(isinstance(i, Iterable) for i in values):
            raise SamariumTypeError("cannot zip a non-iterable")
        self.iters = values
        self.val = zip(*values)

    def __hash__(self) -> int:
        return hash(self.val)

    def __bool__(self) -> bool:
        return True

    def __iter__(self) -> PyIterator[Array]:
        yield from map(Array, self.val)

    def __matmul__(self, other: Any) -> Zip:
        return Zip(*self.iters, other)

    def __str__(self) -> str:
        return f"<Zip@{id(self):x}>"

    def special(self) -> Number:
        return Num(len(self.iters))


class Iterator(Generic[T], Attrs):
    __slots__ = ("val", "length")

    def __init__(self, value: Any) -> None:
        if not isinstance(value, Iterable):
            raise SamariumTypeError("cannot create an Iterator from a non-iterable")
        self.val = iter(value)
        try:
            self.length = Num(len(value.val))
        except (TypeError, AttributeError):
            self.length = NULL

    def __bool__(self) -> bool:
        return True

    def __iter__(self) -> PyIterator[T]:
        yield from self.val

    def __next__(self) -> T:
        return next(self.val)

    def __str__(self) -> str:
        return f"<Iterator@{id(self):x}>"

    def cast(self) -> Number | Null:
        return self.length

    def special(self) -> T:
        return next(self)


class Enum(Attrs):
    __slots__ = ("name", "members")

    def __bool__(self) -> bool:
        return bool(self.members)

    def __init__(self, name: str, **members: Any) -> None:
        self.name = name.removeprefix("sm_")
        self.members: dict[str, Any] = {}

        i = 0
        for k, v in members.items():
            if v is NEXT:
                self.members[k] = Num(i)
                i += 1
            else:
                self.members[k] = v
                if isinstance(v, Number):
                    i = v.val + 1

    def __str__(self) -> str:
        return f"Enum({self.name})"

    def __getattr__(self, name: str) -> Any:
        try:
            return self.members[name]
        except KeyError:
            raise AttributeError(f"'{self.name}''{name}'") from None

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("sm_"):
            raise SamariumTypeError("enum members cannot be modified")
        object.__setattr__(self, name, value)

    def cast(self) -> Table:
        return Table(
            {
                String(k.removeprefix("__").removeprefix("sm_")): v
                for k, v in self.members.items()
            }
        )


class Function(Attrs):
    def __init__(
        self,
        func: Callable[..., Any],
        inst: Any | None = None,
    ) -> None:
        code = func.__code__
        flags = code.co_flags
        self.varargs = bool(flags & 4)
        func.__code__ = func.__code__.replace(
            co_flags=flags & ~4, co_argcount=code.co_argcount + self.varargs
        )
        self.func = func
        self.param_count = len(signature(func).parameters) - self.varargs
        self.inst = inst

    def __str__(self) -> str:
        return get_name(self.func)

    def __call__(self, *args: Any) -> Any:
        for arg in args:
            check_type(arg)
        supplied = len(args)
        posargs, args = args[: self.param_count], args[self.param_count :]
        if self.inst is not None:
            posargs = (self.inst, *posargs)
        if not self.varargs and args:
            raise SamariumTypeError(
                f"too many arguments ({supplied}/{self.param_count})"
            )
        try:
            out = correct_type(
                self.func(*posargs, Array(args))
                if self.varargs
                else self.func(*posargs)
            )
        except TypeError as e:
            errmsg = str(e)
            if m := MISSING_POSARG.search(errmsg):
                raise SamariumTypeError(
                    f"not enough arguments ({supplied}/{supplied + int(m.group(1))})"
                ) from None
            if "positional argument: 'self'" in errmsg:
                raise SamariumTypeError("missing instance") from None
            raise
        return out

    def __hash__(self) -> int:
        return cast(int, self.hash().val)

    def hash(self) -> Number:
        return Num(hash(self.func))

    def special(self) -> Number:
        return Num(self.param_count + self.varargs)


def check_type(obj: Any) -> None:
    if isinstance(obj, property):
        raise SamariumTypeError("cannot use a special method on a type")
    if isinstance(obj, (tuple, GeneratorType)):
        raise SamariumSyntaxError("invalid syntax")


def correct_type(obj: T, *objs: T) -> T | Array | Number | Iterator | Table | Null:
    if objs:
        return Array(map(correct_type, (obj, *objs)))
    if isinstance(
        obj, (Null, Number, String, Slice, Enum, Type, Module, Zip, Function)
    ):
        return obj
    if obj is None:
        return NULL
    if isinstance(obj, bool):
        return Num(obj)
    if isinstance(obj, GeneratorType):
        return Iterator(obj)
    if isinstance(obj, (list, tuple, Array)):
        return Array(map(correct_type, obj))
    if isinstance(obj, Table):
        return Table({correct_type(k): correct_type(v) for k, v in obj.val.items()})
    check_type(obj)
    return obj


def is_valid_index(obj: Attrs, index: Number) -> bool:
    len_ = len(obj.val)
    return -len_ <= index.val < len_ and index.is_int


def param_count(func: Callable) -> int:
    with suppress(AttributeError):
        return func.param_count
    return len(signature(func).parameters) + isinstance(func, MethodType)


def to_chr(code: int) -> str:
    if 0 <= code < 0x110000:
        return chr(code)
    raise SamariumValueError("invalid Unicode code point")


def to_string(obj: Attrs | Callable) -> str:
    return str(obj)
