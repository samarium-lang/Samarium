from __future__ import annotations

from enum import Enum
from os import write
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, cast

from samarium.classes.base import NULL, Array, Attrs, Null, Num, Number, Slice, String
from samarium.exceptions import SamariumIOError, SamariumTypeError, SamariumValueError
from samarium.utils import get_type_name

if TYPE_CHECKING:
    from collections.abc import Iterator


class Mode(Enum):
    READ = "r"
    WRITE = "w"
    READ_WRITE = "r+"
    APPEND = "a"


class FileManager:
    @staticmethod
    def create(path: String) -> Null:
        Path(path.val).touch()
        return NULL

    @staticmethod
    def open(path: String | Number, mode: Mode, *, binary: bool = False) -> File:
        if isinstance(path, Number):
            if mode is Mode.READ_WRITE:
                msg = "cannot open a standard stream in a read & write mode"
                raise SamariumIOError(
                    msg
                )
            if not path.is_int:
                msg = "cannot use non-integers"
                raise SamariumValueError(msg)
        pth = cast(int, path.val) if isinstance(path, Number) else path.val
        f = Path(pth).open(mode.value + "b" * binary)  # noqa: SIM115
        return File(f, mode.name, pth, binary=binary)

    @staticmethod
    def open_binary(path: String, mode: Mode) -> File:
        return FileManager.open(path, mode, binary=True)

    @staticmethod
    def quick(
        path: String | File | Number,
        mode: Mode,
        *,
        data: String | Array | None = None,
        binary: bool = False,
    ) -> String | Array | Null:
        if isinstance(path, String):
            with open(path.val, mode.value + "b" * binary) as f:
                if mode is Mode.READ:
                    if binary:
                        return Array(map(Num, f.read()))
                    return String(f.read())
                if data is None:
                    msg = "missing data"
                    raise SamariumIOError(msg)
                if isinstance(data, Array):
                    bytes_ = b""
                    for i in data.val:
                        try:
                            bytes_ += i.val.to_bytes(1, "big")
                        except AssertionError:
                            msg = "some items in the array are not of type Integer"
                            raise SamariumTypeError(
                                msg
                            ) from None
                    f.write(bytes_)
                else:
                    f.write(data.val)
        elif isinstance(path, Number):
            if not path.is_int:
                msg = "cannot use non-integers"
                raise SamariumValueError(msg)
            if mode in {Mode.APPEND, Mode.WRITE}:
                fd = cast(int, path.val)
                write(fd, str(data).encode())
            else:
                msg = (
                    "reading from file descriptors is "
                    "not supported for quick operations"
                )
                raise SamariumIOError(
                    msg
                )
        else:
            file = path
            if mode is Mode.READ:
                return file.load()
            if data is not None:
                file.save(data)
            else:
                msg = "missing data"
                raise SamariumIOError(msg)
        return NULL


class File(Attrs):
    __slots__ = ("binary", "mode", "path", "val")

    def __init__(self, file: IO, mode: str, path: str | int, *, binary: bool) -> None:
        self.binary = binary
        self.mode = mode
        self.path = path
        self.val = file

    def __bool__(self) -> bool:
        return not self.val.closed

    def __str__(self) -> str:
        return f'File(path:"{self.path}", mode:{self.mode})'

    def __invert__(self) -> Null:
        self.val.close()
        return NULL

    def __iter__(self) -> Iterator[String] | Iterator[Array[Number]]:
        if self.binary:
            for line in self.val:
                yield Array(map(Num, list(line)))
        else:
            yield from map(String, self.val)

    def __getitem__(self, index: Any) -> Array | String | Number | Null:
        if isinstance(index, Slice):
            if index.is_empty():
                return Num(self.val.tell())
            if isinstance(index.step, Number):
                msg = "cannot use step"
                raise SamariumIOError(msg)
            if isinstance(index.start, Number):
                if not isinstance(index.stop, Number):
                    return self.load(index.start)
                if not (index.start.is_int or index.stop.is_int):
                    msg = f"invalid index: {index}"
                    raise SamariumValueError(msg)
                start = cast(int, index.start.val)
                stop = cast(int, index.stop.val)
                current_pos = self.val.tell()
                self.val.seek(start)
                data = self.val.read(stop - start)
                self.val.seek(current_pos)
                if self.binary:
                    if isinstance(data, bytes):
                        data = [*data]
                    return Array(map(Num, data))
                return String(data)
            return self[Slice(Num(0), slice.stop, slice.step)]

        self.val.seek(index.val)
        return NULL

    def load(self, bytes_: Number | None = None) -> String | Array:
        if bytes_ is None:
            bytes_ = Num(-1)
        if not bytes_.is_int:
            msg = "cannot use non-integers"
            raise SamariumValueError(msg)
        val = self.val.read(cast(int, bytes_.val))
        if self.binary:
            return Array(map(Num, val))
        return String(val)

    def save(self, data: String | Array) -> Null:
        if (self.binary and isinstance(data, String)) or (
            not self.binary and isinstance(data, Array)
        ):
            raise SamariumTypeError(get_type_name(data))
        if isinstance(data, Array):
            bytes_ = b""
            for i in data.val:
                try:
                    bytes_ += i.val.to_bytes(1, "big")
                except AssertionError:
                    msg = "some items in the array are not of type Integer"
                    raise SamariumTypeError(
                        msg
                    ) from None
            self.val.write(bytes_)
        else:
            self.val.write(data.val)
        return NULL
