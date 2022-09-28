from __future__ import annotations

from contextlib import contextmanager, suppress
from functools import wraps
from inspect import signature
from re import compile
from secrets import choice, randbelow
from types import FunctionType, GeneratorType
from typing import Any, Callable, Iterable, Iterator

from ..exceptions import (
    NotDefinedError,
    SamariumSyntaxError,
    SamariumTypeError,
    SamariumValueError,
)
from ..utils import (
    ClassProperty,
    LFUCache,
    Singleton,
    get_name,
    get_type_name,
    guard,
    parse_integer,
)


def throw_missing(*_):
    raise SamariumTypeError("missing default parameter value(s)")


class Missing:
    @property
    def type(self) -> None:
        throw_missing()

    @property
    def parent(self) -> None:
        throw_missing()

    @property
    def id(self) -> None:
        throw_missing()


METHODS = (
    "getattr add str sub mul floordiv pow mod and or xor neg pos invert getitem "
    "setitem eq ne ge gt le lt contains hash call iter"
)

for m in METHODS.split():
    setattr(Missing, f"__{m}__", throw_missing)

MISSING = Missing()


class Attrs:
    @ClassProperty
    def id(self) -> String:
        return String(f"{id(self):x}")

    @ClassProperty
    def type(self) -> Type:
        return Type(type(self))

    parent = type


class UserAttrs(Attrs):

    def __init__(self, *args) -> None:
        with suppress(AttributeError):
            self.__entry__(*args)

    def __str__(self) -> str:
        try:
            string = self.__string__
        except AttributeError:
            return f"<{get_type_name(self)}@{self.id}>"
        if string.argc.val != 1:
            raise SamariumTypeError(
                f"{get_type_name(self)}! should only take one argument"
            )
        v = string().val
        if isinstance(v, str):
            return v
        raise SamariumTypeError(f"{get_type_name(self)}! returned a non-string")

    def __bool__(self) -> bool:
        try:
            bit = self.__bit__
        except AttributeError:
            raise NotDefinedError(f"? {get_type_name(self)}")
        if bit.argc.val != 1:
            raise SamariumTypeError(
                f"? {get_type_name(self)} should only take one argument"
            )
        v = bit().val
        if v == 0 or v == 1:
            return bool(v)
        raise SamariumTypeError(f"? {get_type_name(self)} returned a non-bit")

    def __hash__(self) -> int:
        return self.hash.val

    @property
    def special(self) -> Any:
        try:
            special = self.__special__
        except AttributeError:
            raise NotDefinedError(f"{get_type_name(self)}$")
        if special.argc.val != 1:
            raise SamariumTypeError(
                f"{get_type_name(self)}$ should only take one argument"
            )
        return special()

    @property
    def hash(self) -> Integer:
        try:
            hsh = self.__hsh__
        except AttributeError:
            raise NotDefinedError(f"{get_type_name(self)}##")
        if hsh.argc != 1:
            raise SamariumTypeError(
                f"{get_type_name(self)}## should only take one argument"
            )
        v = hsh()
        if isinstance(v, Integer):
            return v
        raise SamariumTypeError(f"{get_type_name(self)}## returned a non-integer")

    @property
    def cast(self) -> Any:
        try:
            cast = self.__cast__
        except AttributeError:
            raise NotDefinedError(f"{get_type_name(self)}%")
        if cast.argc != 1:
            raise SamariumTypeError(
                f"{get_type_name(self)}% should only take one argument"
            )
        return cast()

    @ClassProperty
    def argc(self) -> int:
        return len(signature(self.__init__).parameters)

    @ClassProperty
    def parent(self) -> Array | Type:
        parents = type(self).__bases__
        if len(parents) == 1:
            parent = parents[0]
            if parent is object:
                return self.type
            return Type(parent)
        return Array(map(Type, parents))


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
        if v in Integer.cache:
            return Integer.cache[v]
        return object.__new__(cls)

    def __init__(self, v: Any = None) -> None:
        if isinstance(v, (int, bool)):
            self.val = int(v)
        elif isinstance(v, Integer):
            self.val = v.val
        elif v is None:
            self.val = 0
        elif isinstance(v, String):
            self.val = parse_integer(v.val)
        else:
            raise SamariumTypeError(f"cannot cast {get_type_name(v)} to Integer")
        if v not in Integer.cache:
            Integer.cache[v] = self

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

    def __invert__(self) -> Integer:
        return Integer(~self.val)

    def __pos__(self) -> Integer:
        return self

    def __neg__(self) -> Integer:
        return Integer(-self.val)

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

    def __hash__(self) -> int:
        return self.hash.val

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

    def __contains__(self, element: String) -> bool:
        return element.val in self.val

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

    def __hash__(self) -> int:
        return self.hash.val

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

    def __contains__(self, element: Any) -> bool:
        return element in self.val

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

    def __contains__(self, element: Any) -> bool:
        return element in self.val

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

    def __hash__(self) -> int:
        return self.hash.val

    @property
    def hash(self) -> Integer:
        return Integer(hash(self.val))


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


def correct_type(obj: Any) -> Any:
    if obj is None:
        return NULL
    return obj


def mkslice(start: Any = MISSING, stop: Any = MISSING, step: Any = MISSING) -> Any:
    if stop is step is MISSING:
        if start is None:
            return Slice(NULL, NULL, NULL)
        return start
    missing_none = {MISSING, None}
    start = NULL if start in missing_none else start
    stop = NULL if stop in missing_none else stop
    step = NULL if step in missing_none else step
    return Slice(start, stop, step)


def t(obj: Any = None) -> Any:
    return obj


def check_type(obj: Any) -> None:
    if isinstance(obj, (tuple, GeneratorType)):
        raise SamariumSyntaxError("invalid syntax")


@contextmanager
def modify(
    func: Callable, args: list[Any], argc: int
) -> Iterator[tuple[Callable, list[Any]]]:
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


def function(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args) -> Any:
        for arg in args:
            check_type(arg)
        with modify(func, list(args), argc) as (f, args):
            try:
                result = correct_type(f(*args))
            except TypeError as e:
                errmsg = str(e)
                if "positional argument: 'self'" in errmsg:
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
        return result

    argc = len(signature(func).parameters)

    wrapper.__str__ = lambda: get_name(func)
    wrapper.special = property(lambda: Integer(argc))
    wrapper.argc = Integer(argc)
    wrapper.parent = Type(FunctionType)
    wrapper.type = Type(FunctionType)

    return wrapper
