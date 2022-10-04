from __future__ import annotations

from typing import Any, Iterable
from typing import Iterator as Iter

from ..exceptions import SamariumSyntaxError, SamariumTypeError, SamariumValueError
from .base import NULL, Attrs, Integer, Null, String, Table


class Enum(Attrs):
    __slots__ = ("name", "members")

    def __bool__(self) -> bool:
        return bool(self.members)

    def __init__(self, globals: dict[str, Any], *values_: str) -> None:
        if any(not isinstance(i, str) for i in values_):
            raise SamariumTypeError("enums cannot be constructed from Type")
        name, *values = values_
        self.name = name.removeprefix("sm_")
        self.members: dict[str, Any] = {}

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
                self.members[v] = Integer(i)
                i += 1

    def __str__(self) -> str:
        return f"Enum({self.name})"

    def __getattr__(self, name: str) -> Any:
        try:
            return self.members[name]
        except KeyError:
            raise AttributeError(f"'{self.name}''{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("sm_"):
            raise SamariumTypeError("enum members cannot be modified")
        object.__setattr__(self, name, value)

    @property
    def cast(self) -> Table:
        return Table(
            {
                String(k.removeprefix("__").removeprefix("sm_")): v
                for k, v in self.members.items()
            }
        )


class Iterator(Attrs):
    __slots__ = ("val", "length")

    def __init__(self, value: Any) -> None:
        if not isinstance(value, Iterable):
            raise SamariumTypeError("cannot create an Iterator from a non-iterable")
        self.val = iter(value)
        try:
            self.length = Integer(len(value.val))
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

    @property
    def cast(self) -> Integer | Null:
        return self.length

    @property
    def special(self) -> Any:
        return next(self)
