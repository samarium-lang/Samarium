from __future__ import annotations

import os
import subprocess
from typing import TypeVar

Self = TypeVar("Self", bound="Samarium")


class Samarium:
    def __init__(self, *, file: str) -> None:
        self.file = file
        self.proc: subprocess.Popen[bytes] | None = None
        self._stdout: bytes | None = None
        self._stderr: bytes | None = None

    def __enter__(self: Self) -> Self:
        path = self.file if os.name != 'nt' else self.file.replace("/", "\\")
        self.proc = subprocess.Popen(
            ["samarium", path],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return self

    def __exit__(self, *_):
        assert self.proc
        self.proc.kill()

    def write(self, s: str):
        assert self.proc
        assert self.proc.stdin

        self.proc.stdin.write(s.encode("utf-8"))
        self.proc.stdin.flush()

    @property
    def stdout(self) -> str | None:
        return str(self._stdout, encoding="utf-8")

    @property
    def stderr(self) -> str | None:
        return str(self._stderr, encoding="utf-8")

    @property
    def return_code(self) -> int:
        if self.proc.returncode is None:
            raise ValueError("Has process completed?")
        return self.proc.returncode

    def finalize(self) -> None:
        assert self.proc
        (self._stdout, self._stderr) = self.proc.communicate()
