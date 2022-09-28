import sys
from re import compile

from dahlia import dahlia

from .runtime import Runtime

SINGLE_QUOTED_NAME = compile(r"'(\w+)'")


def handle_exception(exception: Exception):
    exc_type = type(exception)
    name = exc_type.__name__
    if exc_type is NotDefinedError:
        exception = NotDefinedError(
            ".".join(i.removeprefix("sm_") for i in str(exception).split("."))
        )
    if (
        exc_type is TypeError
        and "missing 1 required positional argument: 'self'" in str(exception)
    ):
        exception = SamariumTypeError("missing instance")
    if exc_type is SyntaxError:
        exception = SamariumSyntaxError(
            f"invalid syntax at {int(str(exception).split()[-1][:-1])}"
        )
    elif exc_type in {AttributeError, NameError}:
        names = SINGLE_QUOTED_NAME.findall(str(exception))
        if names == ["entry"]:
            names = ["no entry point defined"]
        exception = NotDefinedError(
            ".".join(i.removeprefix("__").removeprefix("sm_") for i in names)
        )
        name = "NotDefinedError"
    elif exc_type not in {AssertionError, NotDefinedError}:
        name = exc_type.__name__
        if name.startswith("Samarium"):
            name = name.removeprefix("Samarium")
        else:
            name = f"External{name}".replace("ExternalZeroDivision", "Math")
    sys.stderr.write(dahlia(f"&4[{name}] {exception}\n"))
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
