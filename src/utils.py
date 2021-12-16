from __future__ import annotations


class SamariumString(str):

    def smf(self) -> SamariumString:
        for i, char in enumerate(self):
            if char == "$" != self[i - 1]:
                to_format = self.capture_word(i)
                self.replace(to_format, eval(to_format[1:]))
        return self

    def capture_word(self, index: int) -> str:
        return self[index:self[index:].find(" ")]


class SamariumInteger(int):

    @staticmethod
    def from_slashes(value: str) -> SamariumInteger:
        return SamariumInteger(
            "".join(
                ("1" if char == "/" else "0")
                for char in value
            )
        )

    @staticmethod
    def to_slashes(value: int) -> str:
        return "".join(
            ("/" if char == "1" else "\\")
            for char in str(value)
        )

    def __str__(self):
        return SamariumInteger.to_slashes(self)


def _cast(obj: int | str) -> str | int:
    if isinstance(obj, int):
        return chr(obj)
    return ord(obj)


def _input(prompt: str):
    in_ = input(prompt) if prompt else input()
    if set(in_) == {"/", "\\"}:
        return int(in_.translate({47: 49, 92: 48}), 2)
    elif in_.isdigit():
        return int(in_)
    else:
        return in_


def _import(file: str):
    try:
        with open(f"{file}.sm") as f:
            code = f.read()
    except FileNotFoundError:
        _throw(f"File {file}.sm not found")
    else:
        exec(code)


def _throw(msg: str):
    print(f"Error: {msg}")
    exit(1)
