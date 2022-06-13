import sys
from re import findall
from termcolor import colored

from .runtime import Runtime


def handle_exception(exception: Exception):
    exc_type = type(exception)
    name = exc_type.__name__
    if exc_type is SyntaxError:
        exception = SamariumSyntaxError(
            f"invalid syntax at {int(str(exception).split()[-1][:-1])}"
        )
    elif exc_type in {AttributeError, NameError}:
        names = findall(r"'(\w+)'", str(exception))
        if names == ["entry"]:
            names = ["no main function defined"]
        exception = NotDefinedError(".".join(names))
        name = "NotDefinedError"
    elif exc_type not in {AssertionError, NotDefinedError}:
        name = exc_type.__name__
        if name.startswith("Samarium"):
            name = name.removeprefix("Samarium")
        else:
            name = f"External{name}"
    sys.stderr.write(colored(f"[{name}] {exception}\n", "red").replace("_", ""))
    if Runtime.quit_on_error:
        exit(1)


class SamariumError(Exception):
    pass


class NotDefinedError(SamariumError):
    def __init__(self, inp: object, message: str = ""):
        if isinstance(inp, str):
            message = inp
            inp = ""
        else:
            inp = type(inp).__name__
        super().__init__(f"{inp}.{message}" if inp else message)


class SamariumImportError(SamariumError):
    pass


class SamariumSyntaxError(SamariumError):
    pass


class SamariumTypeError(SamariumError):
    pass


class SamariumValueError(SamariumError):
    pass


class SamariumIOError(SamariumError):
    pass
