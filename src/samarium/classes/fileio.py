from __future__ import annotations

from enum import Enum
from os import write
from typing import IO, Any

from samarium.utils import get_type_name

from ..exceptions import SamariumIOError, SamariumTypeError
from .base import NULL, Array, Attrs, Int, Integer, Null, Slice, String


class Mode(Enum):
    READ = "r"
    WRITE = "w"
    READ_WRITE = "r+"
    APPEND = "a"


class FileManager:
    @staticmethod
    def create(path: String) -> Null:
        open(path.val, "x").close()
        return NULL

    @staticmethod
    def open(path: String | Integer, mode: Mode, *, binary: bool = False) -> File:
        if isinstance(path, Integer) and mode is Mode.READ_WRITE:
            raise SamariumIOError(
                "cannot open a standard stream in a read & write mode"
            )
        f = open(path.val, mode.value + "b" * binary)
        return File(f, mode.name, path.val, binary=binary)

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
            with open(path.val, mode.value + "b" * binary) as f:
                if mode is Mode.READ:
                    if binary:
                        return Array(map(Int, f.read()))
                    return String(f.read())
                if data is None:
                    raise SamariumIOError("missing data")
                if isinstance(data, Array):
                    bytes_ = b""
                    for i in data.val:
                        try:
                            bytes_ += i.val.to_bytes(1, "big")
                        except AssertionError:
                            raise SamariumTypeError(
                                "some items in the array are not of type Integer"
                            ) from None
                    f.write(bytes_)
                else:
                    f.write(data.val)
        elif isinstance(path, Integer):
            if mode in {Mode.APPEND, Mode.WRITE}:
                fd = path.val
                write(fd, str(data).encode())
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
        return f"File(path:{self.path}, mode:{self.mode})"

    def __invert__(self) -> Null:
        self.val.close()
        return NULL

    def __getitem__(self, index: Any) -> Array | String | Integer | Null:
        if isinstance(index, Slice):
            if index.is_empty():
                return Int(self.val.tell())
            if isinstance(index.step, Integer):
                raise SamariumIOError("cannot use step")
            if isinstance(index.start, Integer):
                if not isinstance(index.stop, Integer):
                    return self.load(index.start)
                current_pos = self.val.tell()
                self.val.seek(index.start.val)
                data = self.val.read(index.stop.val - index.start.val)
                self.val.seek(current_pos)
                if self.binary:
                    if isinstance(data, bytes):
                        data = [*data]
                    return Array(map(Int, data))
                return String(data)
            return self[Slice(Int(0), slice.stop, slice.step)]
        else:
            self.val.seek(index.val)
            return NULL

    def load(self, bytes_: Integer | None = None) -> String | Array:
        if bytes_ is None:
            bytes_ = Int(-1)
        val = self.val.read(bytes_.val)
        if self.binary:
            return Array(map(Int, val))
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
                    raise SamariumTypeError(
                        "some items in the array are not of type Integer"
                    ) from None
            self.val.write(bytes_)
        else:
            self.val.write(data.val)
        return NULL
