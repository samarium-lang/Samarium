import sys
from re import findall
from termcolor import colored

from .runtime import Runtime


def handle_exception(exception: Exception):
    name = exception.__class__.__name__
    if name == "SyntaxError":
        exception = SamariumSyntaxError(
            f"invalid syntax at {hex(int(str(exception).split()[-1][:-1]))}"
        )
    elif name in {"AttributeError", "NameError"}:
        names = findall(r"'(\w+)'", str(exception))
        if names == ["entry"]:
            names = ["no main function defined"]
        exception = NotDefinedError(".".join(names))
        name = "NotDefinedError"
    elif name not in {"AssertionError", "NotDefinedError"}:
        if name.startswith("Samarium"):
            name = name.removeprefix("Samarium")
        else:
            name = f"External{name}"
    sys.stderr.write(colored(f"[{name}] {exception}\n", "red").replace("_", ""))
    if Runtime.quit_on_error:
        exit(1)


class SamariumError(Exception):
    prefix = ""

    def __init__(self, message: str = ""):
        super().__init__(f"{self.prefix}{message}")


class NotDefinedError(SamariumError):
    def __init__(self, inp: object, message: str = ""):
        if isinstance(inp, str):
            message = inp
            inp = ""
        else:
            inp = inp.__class__.__name__
        super().__init__(f"{inp}." * bool(inp) + f"{message}")


class SamariumImportError(SamariumError):
    prefix = "invalid module: "


class SamariumSyntaxError(SamariumError):
    pass


class SamariumTypeError(SamariumError):
    pass


class SamariumValueError(SamariumError):
    pass


class SamariumIOError(SamariumError):
    pass
