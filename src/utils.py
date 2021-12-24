from __future__ import annotations
from typing import Any


class SMClass:

    def __init__(self, *args):
        self.__ops = []
        self.init_(*args)

    def __str__(self):
        return self.toString_()

    def __special__(self):
        return self.special_()


class SMString(str):

    def __special__(self) -> SMInteger:
        return SMInteger(len(self))


class SMTable:

    def __init__(self, table: dict[Any, Any]):
        self._table = table

    def __special__(self) -> SMArray:
        return SMArray([*self._table.values()])

    def __contains__(self, key: Any) -> SMInteger:
        return SMInteger(key in self._table)

    def __str__(self) -> SMString:
        return SMString(
            "{{" + ", ".join(f"{k} -> {v}" for k, v in self._table.items()) + "}}"
        )

    def __iter__(self):
        yield from self._table

    def __bool__(self) -> SMInteger:
        return SMInteger(bool(self._table))

    def __call__(self, key: Any) -> Any:
        return self._table[key]


class SMArray:

    def __init__(self, array: list[Any]):
        self._array = array

    def __bool__(self) -> SMInteger:
        return SMInteger(bool(self._array))

    def __iter__(self):
        yield from self._array

    def __contains__(self, element: Any) -> bool:
        return element in self._array

    def __special__(self) -> SMInteger:
        return SMInteger(len(self._array))

    def __call__(self, *indexes: SMInteger) -> Any:
        index = [i._value for i in indexes]
        if len(index) == 1:
            return self._array[index[0]]
        else:
            return SMArray(self._array[slice(*index)])

    def __sub__(self, data: int | list[Any]) -> Any | None:
        if isinstance(data, int):
            newarr = self._array.copy()
            return newarr.pop(data)
        elif isinstance(data, list):
            for i in data:
                self._array.remove(i)

    def __add__(self, data: Any) -> SMArray:
        return SMArray(self._array + [data])

    def __mul__(self, data: list[Any]) -> SMArray:
        newarr = self._array.copy()
        newarr.extend(data)
        return SMArray(newarr)

    def __str__(self) -> str:
        return f"{self._array}"


class SMInteger:

    def __init__(self, value: int):
        self._value = value

    def __bool__(self) -> bool:
        return bool(self._value)

    # Arithmetic
    def __add__(self, other: SMInteger) -> SMInteger:
        return SMInteger(self._value + other._value)

    def __sub__(self, other: SMInteger) -> SMInteger:
        return SMInteger(self._value - other._value)

    def __mul__(self, other: SMInteger) -> SMInteger:
        return SMInteger(self._value * other._value)

    def __floordiv__(self, other: SMInteger) -> SMInteger:
        return SMInteger(self._value // other._value)

    def __mod__(self, other: SMInteger) -> SMInteger:
        return SMInteger(self._value % other._value)

    def __pow__(self, other: SMInteger) -> SMInteger:
        return SMInteger(self._value ** other._value)

    # Comparison
    def __eq__(self, other: SMInteger) -> SMInteger:
        return SMInteger(self._value == other._value)

    def __ne__(self, other: SMInteger) -> SMInteger:
        return SMInteger(self._value != other._value)

    def __lt__(self, other: SMInteger) -> SMInteger:
        return SMInteger(self._value < other._value)

    def __gt__(self, other: SMInteger) -> SMInteger:
        return SMInteger(self._value > other._value)

    def __le__(self, other: SMInteger) -> SMInteger:
        return SMInteger(self._value <= other._value)

    def __ge__(self, other: SMInteger) -> SMInteger:
        return SMInteger(self._value >= other._value)

    # Bitwise
    def __and__(self, other: SMInteger) -> SMInteger:
        return SMInteger(self._value & other._value)

    def __or__(self, other: SMInteger) -> SMInteger:
        return SMInteger(self._value | other._value)

    def __xor__(self, other: SMInteger) -> SMInteger:
        return SMInteger(self._value ^ other._value)

    def __invert__(self) -> SMInteger:
        return SMInteger(~self._value)

    def __lshift__(self, other: SMInteger) -> SMInteger:
        return SMInteger(self._value << other._value)

    def __rshift__(self, other: SMInteger) -> SMInteger:
        return SMInteger(self._value >> other._value)

    def __abs__(self) -> SMInteger:
        return SMInteger(abs(self._value))

    def __neg__(self) -> SMInteger:
        return SMInteger(-self._value)

    def __pos__(self) -> SMInteger:
        return SMInteger(+self._value)

    @staticmethod
    def from_slashes(value: str) -> SMInteger:
        return SMInteger(
            int(
                "".join(
                    ("1" if char == "/" else "0")
                    for char in value
                ), 2
            )
        )

    @staticmethod
    def to_slashes(value: int) -> str:
        return "".join(
            ("/" if char == "1" else "\\")
            for char in bin(value)[2:]
        )

    def __str__(self) -> str:
        return SMInteger.to_slashes(self._value)

    def __repr__(self) -> str:
        return str(self)


def _cast(obj: SMInteger | str) -> str | SMInteger:
    if isinstance(obj, SMInteger):
        return chr(obj._value)
    return SMInteger(ord(obj))


def _input(prompt: str = ""):
    in_ = input(prompt)
    if set(in_) == {"/", "\\"}:
        return SMInteger.from_slashes(in_)
    elif in_.isdigit():
        return SMInteger(int(in_))
    else:
        return in_


def _throw(msg: str):
    print(f"Error: {msg}")
    exit(1)
