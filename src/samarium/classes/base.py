from __future__ import annotations

from secrets import choice, randbelow
from types import FunctionType
from typing import Any, Iterable, Iterator

from ..exceptions import NotDefinedError, SamariumTypeError, SamariumValueError
from ..utils import LFUCache, Singleton, get_name, get_type_name, guard, parse_integer


class Attrs:
    @property
    def id(self) -> String:
        return String(f"{id(self):x}")

    @property
    def type(self) -> Type:
        return Type(type(self))

    parent = type


class Type(Attrs):
    __slots__ = ("val",)

    def __init__(self, type_: type) -> None:
        self.val = type_

    def __eq__(self, other: Any) -> Integer:
        if isinstance(other, Type):
            return Integer(self.val == other.val)
        return Integer(False)

    def __ne__(self, other: Any) -> Integer:
        if isinstance(other, Type):
            return Integer(self.val != other.val)
        return Integer(True)

    def __str__(self) -> str:
        if self.val is FunctionType:
            return "Function"
        return get_name(self.val)

    __repr__ = __str__

    def __bool__(self) -> bool:
        return True

    def __call__(self, *args: Any) -> Any:
        if self.val is FunctionType:
            raise SamariumTypeError("cannot instantiate a function")
        if self.val is Module:
            raise SamariumTypeError("cannot instantiate a module")
        return self.val(*args)


class Module(Attrs):
    __slots__ = ("name", "objects")

    def __init__(self, name: str, objects: dict[str, Any]) -> None:
        self.name = name
        self.objects = objects

    def __str__(self) -> str:
        return f"Module[{self.name}]"

    __repr__ = __str__

    def __getattr__(self, key: str) -> Any:
        return self.objects[key]


class Integer(Attrs):
    __slots__ = ("val",)
    cache: LFUCache[Any, Integer] = LFUCache()

    def __new__(cls, v: Any) -> Integer:
        if v in cls.cache:
            return cls.cache[v]
        return object.__new__(cls)

    def __init__(self, v: Any) -> None:
        if v not in Integer.cache:
            Integer.cache[v] = self
        if isinstance(v, (int, bool, float)):
            self.val = int(v)
        elif v is None:
            self.val = 0
        elif isinstance(v, str):
            self.val = parse_integer(v)
        else:
            raise SamariumTypeError(f"cannot cast {get_type_name(v)} to Integer")

    def __bool__(self) -> bool:
        return self.val != 0

    def __str__(self) -> str:
        return str(self.val)

    __repr__ = __str__

    @guard("+")
    def __add__(self, other: Any) -> Integer:
        return Integer(self.val + other.val)

    @guard("-")
    def __sub__(self, other: Any) -> Integer:
        return Integer(self.val - other.val)

    @guard("++")
    def __mul__(self, other: Any) -> Integer:
        return Integer(self.val * other.val)

    @guard("--")
    def __floordiv__(self, other: Any) -> Integer:
        return Integer(self.val // other.val)

    @guard("+++")
    def __pow__(self, other: Any) -> Integer:
        return Integer(self.val ** other.val)

    @guard("---")
    def __mod__(self, other: Any) -> Integer:
        return Integer(self.val % other.val)

    @guard("&")
    def __and__(self, other: Any) -> Integer:
        return Integer(self.val & other.val)

    @guard("|")
    def __or__(self, other: Any) -> Integer:
        return Integer(self.val | other.val)

    @guard("^")
    def __xor__(self, other: Any) -> Integer:
        return Integer(self.val ^ other.val)

    def __not__(self) -> Integer:
        return Integer(~self.val)

    def __pos__(self) -> Integer:
        return self

    def __eq__(self, other: Any) -> Integer:
        if isinstance(other, Integer):
            return Integer(self.val == other.val)
        return Integer(False)

    def __ne__(self, other: Any) -> Integer:
        if isinstance(other, Integer):
            return Integer(self.val != other.val)
        return Integer(True)

    @guard(">")
    def __gt__(self, other: Any) -> Integer:
        return Integer(self.val > other.val)

    @guard(">:")
    def __ge__(self, other: Any) -> Integer:
        return Integer(self.val >= other.val)

    @guard("<")
    def __lt__(self, other: Any) -> Integer:
        return Integer(self.val < other.val)

    @guard("<:")
    def __le__(self, other: Any) -> Integer:
        return Integer(self.val <= other.val)

    @property
    def cast(self) -> String:
        return String(chr(self.val))

    @property
    def hash(self) -> Integer:
        return Integer(hash(self.val))

    @property
    def random(self) -> Integer:
        v = self.val
        if not v:
            return self
        elif v > 0:
            return Integer(randbelow(v))
        else:
            return Integer(-randbelow(v) - 1)

    @property
    def special(self) -> String:
        return String(f"{self.val:b}")


class String(Attrs):
    __slots__ = ("val",)

    def __init__(self, value: Any = "") -> None:
        self.val = str(value)

    def __contains__(self, element: String) -> Integer:
        return Integer(element.val in self.val)

    def __iter__(self) -> Iterator[String]:
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

    @guard("++")
    def __mul__(self, other: Any) -> String:
        return String(self.val * other.val)

    def __eq__(self, other: Any) -> Integer:
        return Integer(self.val == other.val)

    def __ne__(self, other: Any) -> Integer:
        return Integer(self.val != other.val)

    @guard(">")
    def __gt__(self, other: Any) -> Integer:
        return Integer(self.val > other.val)

    @guard(">:")
    def __ge__(self, other: Any) -> Integer:
        return Integer(self.val >= other.val)

    @guard("<")
    def __lt__(self, other: Any) -> Integer:
        return Integer(self.val < other.val)

    @guard("<:")
    def __le__(self, other: Any) -> Integer:
        return Integer(self.val <= other.val)

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

    @property
    def cast(self) -> Integer:
        if len(self.val) != 1:
            raise SamariumTypeError(f"cannot cast a string of length {len(self.val)}")
        return Integer(ord(self.val))

    @property
    def hash(self) -> Integer:
        return Integer(hash(self.val))

    @property
    def random(self) -> String:
        return String(choice(self.val))

    @property
    def special(self) -> Integer:
        return Integer(len(self.val))


class Array(Attrs):
    __slots__ = ("val",)

    def __init__(self, value: Any = None) -> None:
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
        return "[{}]".format(", ".join(map(repr, self.val)))

    __repr__ = __str__

    def __bool__(self) -> bool:
        return self.val != []

    def __iter__(self) -> Iterator[Any]:
        yield from self.val

    def __contains__(self, element: Any) -> Integer:
        return Integer(element in self.val)

    def __eq__(self, other: Any) -> Integer:
        if isinstance(other, Array):
            return Integer(self.val == other.val)
        return Integer(False)

    def __ne__(self, other: Any) -> Integer:
        if isinstance(other, Array):
            return Integer(self.val != other.val)
        return Integer(True)

    @guard(">")
    def __gt__(self, other: Any) -> Integer:
        return Integer(self.val > other.val)

    @guard(">:")
    def __ge__(self, other: Any) -> Integer:
        return Integer(self.val >= other.val)

    @guard("<")
    def __lt__(self, other: Any) -> Integer:
        return Integer(self.val < other.val)

    @guard("<:")
    def __le__(self, other: Any) -> Integer:
        return Integer(self.val <= other.val)

    def __getitem__(self, index: Any) -> Any:
        if isinstance(index, Integer):
            return self.val[index.val]
        if isinstance(index, Slice):
            return Array(self.val[index.val])
        raise SamariumTypeError(f"invalid index: {index}")

    def __setitem__(self, index: Any, value: Any) -> None:
        if not isinstance(self, (Integer, Slice)):
            raise SamariumTypeError(f"invalid index: {index}")
        self.val[index.val] = value

    @guard("+")
    def __add__(self, other: Any) -> Array:
        return Array(self.val + other.val)

    def __sub__(self, other: Any) -> Array:
        new_array = self.val.copy()
        if isinstance(other, Array):
            for i in other:
                new_array.remove(i)
        elif isinstance(other, Integer):
            new_array.pop(other.val)
        else:
            raise NotDefinedError(f"Array - {get_type_name(other)}")
        return Array(new_array)

    def __mul__(self, other: Any) -> Array:
        if isinstance(other, Integer):
            return Array(self.val * other.val)
        raise NotDefinedError(f"Array ++ {get_type_name(other)}")

    @property
    def random(self) -> Any:
        if not self.val:
            raise SamariumValueError("array is empty")
        return choice(self.val)

    @property
    def special(self) -> Integer:
        return Integer(len(self.val))


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
                        assert isinstance(e, Array)
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
            ", ".join(f"{k!r} -> {v!r}" for k, v in self.val.items())
        )

    def __bool__(self) -> bool:
        return self.val != {}

    def __getitem__(self, key: Any) -> Any:
        try:
            return self.val[key]
        except KeyError:
            raise SamariumValueError(f"key not found: {key}")

    def __setitem__(self, key: Any, value: Any) -> None:
        self.val[key] = value

    def __iter__(self) -> Iterator[Any]:
        yield from self.val.keys()

    def __contains__(self, element: Any) -> Integer:
        return Integer(element in self.val)

    def __eq__(self, other: Any) -> Integer:
        if isinstance(other, Table):
            return Integer(self.val == other.val)
        return Integer(False)

    def __ne__(self, other: Any) -> Integer:
        if isinstance(other, Table):
            return Integer(self.val != other.val)
        return Integer(True)

    @guard("+")
    def __add__(self, other: Any) -> Table:
        return Table(self.val | other.val)

    def __sub__(self, other: Any) -> Table:
        c = self.val.copy()
        try:
            del c[other]
        except KeyError:
            raise SamariumValueError(f"key not found: {other}")
        return Table(c)

    @property
    def random(self) -> Any:
        if not self.val:
            raise SamariumValueError("table is empty")
        return choice(list(self.val.keys()))

    @property
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

    @property
    def hash(self) -> int:
        return hash(self.val)


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
        self.tup = start, stop, step
        self.range = range(
            self.tup[0] or 0,
            I64_MAX if self.tup[1] is None else self.tup[1],
            self.tup[2] or 1,
        )
        self.val = slice(*self.tup)

    def __iter__(self) -> Iterator[Integer]:
        yield from map(Integer, self.range)

    def __contains__(self, value: Integer) -> bool:
        return value in self.range

    def __getitem__(self, index: Integer) -> Integer:
        return Integer(self.range[index.val])

    def __str__(self) -> str:
        start, stop, step = self.tup
        if self.is_empty():
            return "<<>>"
        string = ""
        if start is not NULL:
            string += repr(start)
            if stop is step is NULL:
                string += ".."
        if stop is not NULL:
            string += f"..{stop!r}"
        if step is not NULL:
            if stop is NULL:
                string += ".."
            string += f"..{step!r}"
        return f"<<{string}>>"

    __repr__ = __str__

    def __eq__(self, other: Any) -> Integer:
        if isinstance(other, Slice):
            return Integer(self.tup == other.tup)
        return Integer(False)

    def __ne__(self, other: Any) -> Integer:
        if isinstance(other, Slice):
            return Integer(self.tup != other.tup)
        return Integer(True)

    @property
    def random(self) -> Integer:
        return Integer(choice(self.range))

    @property
    def special(self) -> Integer:
        return Integer(len(self.range))

    def is_empty(self) -> bool:
        return self.start is self.stop is self.step is NULL
