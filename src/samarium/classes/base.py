from __future__ import annotations

from collections.abc import Callable
from functools import lru_cache
from inspect import signature
from secrets import choice, randbelow
from types import FunctionType
from typing import Any, Iterable
from typing import Iterator as Iter

from ..exceptions import NotDefinedError, SamariumTypeError, SamariumValueError
from ..utils import (
    ClassProperty,
    Singleton,
    get_name,
    get_type_name,
    parse_integer,
    smformat,
)


def functype_repr(obj: Any) -> str:
    return (
        get_name(obj)
        if isinstance(obj, FunctionType)
        or (isinstance(obj, type) and issubclass(obj, UserAttrs))
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
                return function(self, Int(default))
            raise NotDefinedError(f"{Ts.__name__} {operator} {To.__name__}")

        return wrapper

    return decorator


def throw_missing(*_) -> None:
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
    "getattr add str sub mul floordiv pow mod and or xor neg pos invert getitem "
    "setitem eq ne ge gt le lt contains hash call iter"
)

for m in METHODS.split():
    setattr(Missing, f"__{m}__", throw_missing)

MISSING = Missing()
NEXT = object()


class Attrs:
    @classmethod
    def id(cls) -> String:
        return String(f"{id(cls):x}")

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

    __string__.argc = 1

    def __str__(self) -> str:
        string = self.__string__
        if string.argc != 1:
            raise SamariumTypeError(
                f"{get_type_name(self)}! should only take one argument"
            )
        v = string().val
        if isinstance(v, str):
            return v
        raise SamariumTypeError(f"{get_type_name(self)}! returned a non-string")

    def __bit__(self) -> Integer:
        raise NotDefinedError(f"? {get_type_name(self)}")

    __bit__.argc = 1

    def __bool__(self) -> bool:
        bit = self.__bit__
        if bit.argc != 1:
            raise SamariumTypeError(
                f"? {get_type_name(self)} should only take one argument"
            )
        v = bit().val
        if v in (0, 1):
            return bool(v)
        raise SamariumTypeError(f"? {get_type_name(self)} returned a non-bit")

    def __hash__(self) -> int:
        return self.hash().val

    def __special__(self) -> Any:
        raise NotDefinedError(f"{get_type_name(self)}$")

    __special__.argc = 1

    def special(self) -> Any:
        special = self.__special__
        if special.argc != 1:
            raise SamariumTypeError(
                f"{get_type_name(self)}$ should only take one argument"
            )
        return special()

    def __hsh__(self) -> Integer:
        raise NotDefinedError(f"{get_type_name(self)}##")

    __hsh__.argc = 1

    def hash(self) -> Integer:
        hsh = self.__hsh__
        if hsh.argc != 1:
            raise SamariumTypeError(
                f"{get_type_name(self)}## should only take one argument"
            )
        v = hsh()
        if isinstance(v, Integer):
            return v
        raise SamariumTypeError(f"{get_type_name(self)}## returned a non-integer")

    def __cast__(self) -> Any:
        raise NotDefinedError(f"{get_type_name(self)}%")

    __cast__.argc = 1

    def cast(self) -> Any:
        cast = self.__cast__
        if cast.argc != 1:
            raise SamariumTypeError(
                f"{get_type_name(self)}% should only take one argument"
            )
        return cast()

    def __random__(self) -> Integer:
        raise NotDefinedError(f"{get_type_name(self)}??")

    __random__.argc = 1

    def random(self) -> Any:
        random = self.__random__
        if random.argc != 1:
            raise SamariumTypeError(
                f"{get_type_name(self)}?? should only take one argument"
            )
        return random()

    @ClassProperty
    def argc(self) -> int:
        return len(signature(self.__init__).parameters)

    @classmethod
    def parent(cls) -> Array | Type:
        parents = cls.__bases__
        if len(parents) == 1:
            parent = parents[0]
            if parent is object:
                return Type(cls)
            return Type(parent)
        return Array(map(Type, parents))


class Type(Attrs):
    __slots__ = ("val",)

    def __init__(self, type_: type) -> None:
        self.val = type_

    def __eq__(self, other: Any) -> Integer:
        if isinstance(other, Type):
            return Int(self.val == other.val)
        return Int(self.val == other)

    def __ne__(self, other: Any) -> Integer:
        if isinstance(other, Type):
            return Int(self.val != other.val)
        return Int(True)

    def __str__(self) -> str:
        if self.val is FunctionType:
            return "Function"
        return get_name(self.val)

    __repr__ = __str__

    def __bool__(self) -> bool:
        return True

    def __hash__(self) -> int:
        return hash(self.val)

    def __call__(self, *args: Any) -> Any:
        if self.val is FunctionType:
            raise SamariumTypeError("cannot instantiate a function")
        if self.val is Module:
            raise SamariumTypeError("cannot instantiate a module")
        if self.val is Type:
            raise SamariumTypeError("cannot instantiate a type")
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


class Integer(Attrs):
    __slots__ = ("val",)

    def __init__(self, v: Any = None) -> None:
        if isinstance(v, (float, int, bool)):
            self.val = int(v)
        elif isinstance(v, Integer):
            self.val = v.val
        elif v is None:
            self.val = 0
        elif isinstance(v, String):
            self.val = parse_integer(v.val) if v else 0
        else:
            raise SamariumTypeError(f"cannot cast {get_type_name(v)} to Integer")

    def __bool__(self) -> bool:
        return self.val != 0

    def __str__(self) -> str:
        return str(self.val)

    __repr__ = __str__

    @guard("+", default=1)
    def __add__(self, other: Any) -> Integer:
        return Int(self.val + other.val)

    @guard("-", default=1)
    def __sub__(self, other: Any) -> Integer:
        return Int(self.val - other.val)

    @guard("++", default=2)
    def __mul__(self, other: Any) -> Integer:
        return Int(self.val * other.val)

    @guard("--", default=2)
    def __floordiv__(self, other: Any) -> Integer:
        return Int(self.val // other.val)

    @guard("+++", default=2)
    def __pow__(self, other: Any) -> Integer:
        return Int(self.val ** other.val)

    @guard("---", default=2)
    def __mod__(self, other: Any) -> Integer:
        return Int(self.val % other.val)

    @guard("&")
    def __and__(self, other: Any) -> Integer:
        return Int(self.val & other.val)

    @guard("|")
    def __or__(self, other: Any) -> Integer:
        return Int(self.val | other.val)

    @guard("^")
    def __xor__(self, other: Any) -> Integer:
        return Int(self.val ^ other.val)

    def __invert__(self) -> Integer:
        return Int(~self.val)

    def __pos__(self) -> Integer:
        return self

    def __neg__(self) -> Integer:
        return Int(-self.val)

    def __eq__(self, other: Any) -> Integer:
        if isinstance(other, Integer):
            return Int(self.val == other.val)
        return Int(False)

    def __ne__(self, other: Any) -> Integer:
        if isinstance(other, Integer):
            return Int(self.val != other.val)
        return Int(True)

    @guard(">", default=0)
    def __gt__(self, other: Any) -> Integer:
        return Int(self.val > other.val)

    @guard(">:", default=0)
    def __ge__(self, other: Any) -> Integer:
        return Int(self.val >= other.val)

    @guard("<", default=0)
    def __lt__(self, other: Any) -> Integer:
        return Int(self.val < other.val)

    @guard("<:", default=0)
    def __le__(self, other: Any) -> Integer:
        return Int(self.val <= other.val)

    def __hash__(self) -> int:
        return self.hash().val

    def cast(self) -> String:
        return String(to_chr(self.val))

    def hash(self) -> Integer:
        return Int(hash(self.val))

    def random(self) -> Integer:
        v = self.val
        if not v:
            return self
        elif v > 0:
            return Int(randbelow(v))
        return Int(-randbelow(v) - 1)

    def special(self) -> String:
        return String(f"{self.val:b}")


Int = lru_cache(1024)(Integer)


class String(Attrs):
    __slots__ = ("val",)

    def __init__(self, value: Any = "") -> None:
        self.val = to_string(value)

    def __contains__(self, element: String) -> bool:
        return element.val in self.val

    def __iter__(self) -> Iter[String]:
        yield from map(String, self.val)

    def __bool__(self) -> bool:
        return self.val != ""

    def __str__(self) -> str:
        return self.val

    def __repr__(self) -> str:
        return f'"{self}"'

    @guard("+")
    def __add__(self, other: Any) -> String:
        return String(self.val + other.val)

    @guard("-")
    def __sub__(self, other: Any) -> String:
        return String(self.val.replace(other.val, ""))

    def __mul__(self, other: Any) -> String:
        if isinstance(other, Integer):
            return String(self.val * other.val)
        raise NotDefinedError(f"String ++ {get_type_name(other)}")

    def __mod__(self, other: Any) -> String:
        if isinstance(other, (String, Array, Table)):
            return String(smformat(self.val, other.val))
        raise NotDefinedError(f"String --- {get_type_name(other)}")

    def __eq__(self, other: Any) -> Integer:
        return Int(self.val == other.val)

    def __ne__(self, other: Any) -> Integer:
        return Int(self.val != other.val)

    @guard(">")
    def __gt__(self, other: Any) -> Integer:
        return Int(self.val > other.val)

    @guard(">:")
    def __ge__(self, other: Any) -> Integer:
        return Int(self.val >= other.val)

    @guard("<")
    def __lt__(self, other: Any) -> Integer:
        return Int(self.val < other.val)

    @guard("<:")
    def __le__(self, other: Any) -> Integer:
        return Int(self.val <= other.val)

    def __getitem__(self, index: Integer | Slice) -> String:
        if isinstance(index, (Integer, Slice)):
            return String(self.val[index.val])
        raise SamariumTypeError(f"invalid index: {index}")

    def __setitem__(self, index: Integer | Slice, value: String) -> None:
        if not isinstance(index, (Integer, Slice)):
            raise SamariumTypeError(f"invalid index: {index}")
        string = [*self.val]
        string[index.val] = value.val
        self.val = "".join(string)

    def __hash__(self) -> int:
        return self.hash().val

    def __matmul__(self, other: Any) -> Zip:
        return Zip(self, other)

    def cast(self) -> Array | Integer:
        if len(self.val) == 1:
            return Int(ord(self.val))
        return Array(Int(ord(i)) for i in self.val)

    def hash(self) -> Integer:
        return Int(hash(self.val))

    def random(self) -> String:
        return String(choice(self.val))

    def special(self) -> Integer:
        return Int(len(self.val))


class Array(Attrs):
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
                raise SamariumValueError("cannot convert an infinite Slice to Array")
            self.val = list(value.range)
        elif isinstance(value, Iterable):
            self.val = [*value]
        else:
            raise SamariumTypeError(f"cannot cast {get_type_name(value)} to Array")

    def __str__(self) -> str:
        return "[{}]".format(", ".join(map(functype_repr, self.val)))

    __repr__ = __str__

    def __bool__(self) -> bool:
        return self.val != []

    def __iter__(self) -> Iter[Any]:
        yield from self.val

    def __contains__(self, element: Any) -> bool:
        return element in self.val

    def __eq__(self, other: Any) -> Integer:
        if isinstance(other, Array):
            return Int(self.val == other.val)
        return Int(False)

    def __ne__(self, other: Any) -> Integer:
        if isinstance(other, Array):
            return Int(self.val != other.val)
        return Int(True)

    @guard(">")
    def __gt__(self, other: Any) -> Integer:
        return Int(self.val > other.val)

    @guard(">:")
    def __ge__(self, other: Any) -> Integer:
        return Int(self.val >= other.val)

    @guard("<")
    def __lt__(self, other: Any) -> Integer:
        return Int(self.val < other.val)

    @guard("<:")
    def __le__(self, other: Any) -> Integer:
        return Int(self.val <= other.val)

    def __getitem__(self, index: Any) -> Any:
        if isinstance(index, Integer):
            return self.val[index.val]
        if isinstance(index, Slice):
            return Array(self.val[index.val])
        raise SamariumTypeError(f"invalid index: {index}")

    def __setitem__(self, index: Any, value: Any) -> None:
        if not isinstance(index, (Integer, Slice)):
            raise SamariumTypeError(f"invalid index: {index}")
        self.val[index.val] = value

    @guard("+")
    def __add__(self, other: Any) -> Array:
        return Array(self.val + other.val)

    def __sub__(self, other: Any) -> Any:
        new_array = self.val.copy()
        if isinstance(other, Array):
            for i in other:
                new_array.remove(i)
        elif isinstance(other, Integer):
            new_array.pop(other.val)
        elif other is NULL:
            return self.val.pop()
        else:
            raise NotDefinedError(f"Array - {get_type_name(other)}")
        return Array(new_array)

    def __mul__(self, other: Any) -> Array:
        if isinstance(other, Integer):
            return Array(self.val * other.val)
        raise NotDefinedError(f"Array ++ {get_type_name(other)}")

    def __matmul__(self, other: Any) -> Zip:
        return Zip(self, other)

    def cast(self) -> String:
        s = ""
        for i in self.val:
            if isinstance(i, Integer):
                s += to_chr(i.val)
            else:
                raise SamariumTypeError("array contains non-integers")
        return String(s)

    def random(self) -> Any:
        if not self.val:
            raise SamariumValueError("array is empty")
        return choice(self.val)

    def special(self) -> Integer:
        return Int(len(self.val))


class Table(Attrs):
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
            raise SamariumTypeError(f"cannot cast {get_type_name(value)} to Table")

    def __str__(self) -> str:
        return "{{{{{}}}}}".format(
            ", ".join(
                f"{functype_repr(k)} -> {functype_repr(v)}" for k, v in self.val.items()
            )
        )

    def __bool__(self) -> bool:
        return self.val != {}

    def __getitem__(self, key: Any) -> Any:
        try:
            return self.val[key]
        except KeyError:
            raise SamariumValueError(f"key not found: {key}") from None

    def __setitem__(self, key: Any, value: Any) -> None:
        self.val[key] = value

    def __iter__(self) -> Iter[Any]:
        yield from self.val.keys()

    def __contains__(self, element: Any) -> bool:
        return element in self.val

    def __eq__(self, other: Any) -> Integer:
        if isinstance(other, Table):
            return Int(self.val == other.val)
        return Int(False)

    def __ne__(self, other: Any) -> Integer:
        if isinstance(other, Table):
            return Int(self.val != other.val)
        return Int(True)

    @guard("+")
    def __add__(self, other: Any) -> Table:
        return Table(self.val | other.val)

    def __sub__(self, other: Any) -> Table:
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

    def special(self) -> Array:
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
        return self.hash().val

    def hash(self) -> Integer:
        return Int(hash(self.val))


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
        self.range = range(
            self.tup[0] or 0,
            I64_MAX if self.tup[1] is None else self.tup[1],
            self.tup[2] or 1,
        )
        self.val = slice(*self.tup)

    def __bool__(self) -> bool:
        return bool(self.range)

    def __iter__(self) -> Iter[Integer]:
        yield from map(Int, self.range)

    def __contains__(self, value: Integer) -> bool:
        return value.val in self.range

    def __getitem__(self, index: Integer) -> Integer:
        return Int(self.range[index.val])

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

    def __eq__(self, other: Any) -> Integer:
        if isinstance(other, Slice):
            return Int(self.tup == other.tup)
        return Int(False)

    def __ne__(self, other: Any) -> Integer:
        if isinstance(other, Slice):
            return Int(self.tup != other.tup)
        return Int(True)

    def random(self) -> Integer:
        return Int(choice(self.range))

    def special(self) -> Integer:
        return Int(len(self.range))

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

    def __iter__(self) -> Iter[Array]:
        yield from map(Array, self.val)

    def __matmul__(self, other: Any) -> Zip:
        return Zip(*self.iters, other)

    def __str__(self) -> str:
        return f"<Zip@{id(self):x}>"

    def special(self) -> Integer:
        return Int(len(self.iters))


class Iterator(Attrs):
    __slots__ = ("val", "length")

    def __init__(self, value: Any) -> None:
        if not isinstance(value, Iterable):
            raise SamariumTypeError("cannot create an Iterator from a non-iterable")
        self.val = iter(value)
        try:
            self.length = Int(len(value.val))
        except (TypeError, AttributeError):
            self.length = NULL

    def __bool__(self) -> bool:
        return True

    def __iter__(self) -> Iter[Any]:
        yield from self.val

    def __next__(self) -> Any:
        return next(self.val)

    def __str__(self) -> str:
        return f"<Iterator@{id(self):x}>"

    def cast(self) -> Integer | Null:
        return self.length

    def special(self) -> Any:
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
                self.members[k] = Int(i)
                i += 1
            else:
                self.members[k] = v
                if isinstance(v, Integer):
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


def to_chr(code: int) -> str:
    if code >= 0x110000:
        raise SamariumValueError("invalid Unicode code point")
    return chr(code)


def to_string(obj: Attrs | Callable) -> str:
    if isinstance(obj, FunctionType):
        return ".".join(i.removeprefix("sm_") for i in obj.__qualname__.split("."))
    return str(obj)
