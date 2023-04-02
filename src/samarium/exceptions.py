import sys
from re import compile

from dahlia import Dahlia

from .runtime import Runtime

DAHLIA = Dahlia()
NDE_TYPES = {AttributeError, NameError, UnboundLocalError}

ARG_NOT_ITER = compile(r"argument of type '(\w+)' is not iterable")
BAD_OP = compile(
    r"'(.+)' not supported between instances of '(\w+)' and '(\w+)'"
    r"|unsupported operand type\(s\) for (.+): '(\w+)' and '(\w+)'"
)
BAD_UOP = compile(r"bad operand type for unary (.+): '(\w+)'")
NO_GETITEM = compile(r"'(\w+)' object is not subscriptable")
NO_SETITEM = compile(r"'(\w+)' object does not support item assignment")
NOT_CALLITER = compile(r"'(\w+)' object is not (\w+)")
OP_MAP = {
    ">=": ">:",
    "<=": "<:",
    "/": "--",
    "%": "---",
    "*": "++",
    "@": "><",
    "** or pow()": "+++",
}
SINGLE_QUOTED_NAME = compile(r"'(\w+)'")


def clear_name(name: str) -> str:
    return name.removeprefix("__").removeprefix("sm_")


def handle_exception(exception: Exception) -> None:
    exc_type = type(exception)
    errmsg = str(exception)
    name = ""
    if exc_type is NotDefinedError:
        exception = NotDefinedError(".".join(map(clear_name, errmsg.split("."))))
    if (
        exc_type is TypeError
        and "missing 1 required positional argument: 'self'" in errmsg
    ):
        exception = SamariumTypeError("missing instance")
    elif m := BAD_OP.match(errmsg):
        op, lhs, rhs = filter(None, m.groups())
        op = OP_MAP.get(op, op)
        exc_type = NotDefinedError
        exception = exc_type(f"{clear_name(lhs)} {op} {clear_name(rhs)}")
    elif m := BAD_UOP.match(errmsg):
        op, type_ = m.groups()
        exc_type = NotDefinedError
        exception = exc_type(f"{op}{clear_name(type_)}")
    elif m := ARG_NOT_ITER.match(errmsg):
        exc_type = NotDefinedError
        type_ = clear_name(m.group(1))
        exception = exc_type(f"->? {type_}")
    elif m := NO_GETITEM.match(errmsg):
        exc_type = NotDefinedError
        type_ = clear_name(m.group(1))
        exception = exc_type(f"{type_}<<>>")
    elif m := NO_SETITEM.match(errmsg):
        exc_type = NotDefinedError
        type_ = clear_name(m.group(1))
        exception = exc_type(f"{type_}<<>>:")
    elif m := NOT_CALLITER.match(errmsg):
        exc_type = NotDefinedError
        type_ = clear_name(m.group(1))
        template = "... _ ->? {}" if m.group(2) == "iterable" else "{}()"
        exception = exc_type(template.format(type_))
    elif exc_type is SyntaxError:
        exception = SamariumSyntaxError(
            f"invalid syntax at {int(errmsg.split()[-1][:-1])}"
        )
    elif exc_type in NDE_TYPES:
        names = SINGLE_QUOTED_NAME.findall(errmsg)
        exc_type = NotDefinedError
        exception = exc_type(
            f"{clear_name(names[0])}<<>>{':' * (names[1] == '__setitem__')}"
            if len(names) >= 2 and names[1] in {"__getitem__", "__setitem__"}
            else ".".join(map(clear_name, names))
        )
    elif exc_type not in {AssertionError, NotDefinedError}:
        name = exc_type.__name__
        if name.startswith("Samarium"):
            name = name.removeprefix("Samarium")
        else:
            name = f"Python{name}".replace("PythonZeroDivision", "Math")
    name = name or exc_type.__name__
    DAHLIA.print(f"&4[{name}] {exception}", file=sys.stderr)
    if Runtime.quit_on_error:
        sys.exit(1)


class SamariumError(Exception):
    pass


class NotDefinedError(SamariumError):
    def __init__(self, inp: object, message: str = "") -> None:
        if isinstance(inp, str):
            message = inp
            inp = ""
        else:
            inp = type(inp).__name__
        super().__init__(f"{inp}.{message}" if inp else message)


class SamariumImportError(SamariumError):
    pass


class SamariumSyntaxError(SamariumError):
    def __init__(self, msg: str) -> None:
        DAHLIA.print(f"&4[SyntaxError] {msg}", file=sys.stderr)
        sys.exit(1)


class SamariumTypeError(SamariumError):
    pass


class SamariumValueError(SamariumError):
    pass


class SamariumIOError(SamariumError):
    pass


class SamariumRecursionError(SamariumError):
    pass
