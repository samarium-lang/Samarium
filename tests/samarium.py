from __future__ import annotations

from functools import cached_property
import subprocess
from typing import IO, TypeVar

Self = TypeVar("Self")


class Samarium:
    def __init__(self, *, file: str) -> None:
        self.file = file
        self.proc = None

    def __enter__(self: Self) -> Self:
        self.proc = subprocess.Popen(
            ["samarium", self.file],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return self

    def __exit__(self, *_):
        assert self.proc
        self.proc.kill()

    def write(self, s: str):
        if self.proc is None:
            return ValueError(
                "Cannot write to stdin because the process has not started. Did you use a context manager?"
            )

        self.proc.stdin.write(s.encode("utf-8"))
        self.proc.stdin.flush()

    @staticmethod
    def decode(buf: IO[bytes] | None) -> str | None:
        if buf is None:
            return None
        return str(buf.read(), encoding="utf-8")

    @cached_property
    def stdout(self) -> str | None:
        return self.decode(self.proc.stdout)

    @cached_property
    def stderr(self) -> str | None:
        return self.decode(self.proc.stderr)

    def assert_return_code(self, code: int) -> int:
        self.proc.communicate()
        assert self.proc.returncode == code
