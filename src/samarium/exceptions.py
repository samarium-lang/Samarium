import sys

from .runtime import Runtime


def handle_exception(exception: Exception):
    name = exception.__class__.__name__
    if name == "SyntaxError":
        exception = SamariumSyntaxError(
            f"invalid syntax at {hex(int(str(exception).split()[-1][:-1]))}"
        )
    if name not in {"SyntaxError", "NotDefinedError", "AssertionError"}:
        if name.startswith("Samarium"):
            name = name.removeprefix("Samarium")
        else:
            name = f"External{name}"
    sys.stderr.write(f"\033[31m[{name}] {exception}\033[0m\n".replace("_", ""))
    if Runtime.quit_on_error:
        exit(1)


class NotDefinedError(Exception):
    def __init__(self, class_, message: str):
        self.class_ = class_.__class__.__name__
        super().__init__(f"{self.class_}.{message}")


class SamariumError(Exception):
    blank = ""
    prefix = ""

    def __init__(self, message: str = ""):
        super().__init__(f"{self.prefix}{message}" if message else self.blank)


class SamariumImportError(SamariumError):
    blank = "import error"
    prefix = "invalid module: "


class SamariumSyntaxError(SamariumError):
    blank = "invalid syntax"


class SamariumTypeError(SamariumError):
    blank = "invalid type"


class SamariumValueError(SamariumError):
    blank = "invalid value"


class SamariumIOError(SamariumError):
    pass
