from __future__ import annotations


class SMString(str):

    def smf(self) -> SMString:
        for i, char in enumerate(self):
            if char == "$" != self[i - 1]:
                to_format = self.capture_word(i)
                self.replace(to_format, eval(f"{to_format[1:]}_"))
        return self

    def capture_word(self, index: int) -> str:
        return self[index:self[index:].find(" ")]


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

    def __str__(self):
        return SMInteger.to_slashes(self._value)


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
