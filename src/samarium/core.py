from . import exceptions
import os
import sys
from contextlib import contextmanager
from datetime import datetime
from .objects import (
    assert_smtype, class_attributes, smhash, verify_type,
    Class, Type, Slice, Null, String, Integer, Module,
    Table, Array, Mode, FileManager, File
)
from secrets import randbelow
from time import sleep as _sleep
from .tokenizer import tokenize
from .transpiler import Transpiler, CodeHandler
from typing import Union

Castable = Union[Integer, String]
MODULE_NAMES = ["math", "random", "iter", "collections", "types", "string"]


class Runtime:
    frozen: list[str] = []
    import_level = 0


def dtnow() -> Array:
    utcnow = datetime.utcnow()
    now = [*datetime.now().timetuple()]
    utcnow_tl = [*datetime.utcnow().timetuple()]
    tz = [now[3] - utcnow_tl[3], now[4] - utcnow_tl[4]]
    utcnow_tl = utcnow_tl[:-3] + [utcnow.microsecond // 1000] + tz
    return Array([Integer(i) for i in utcnow_tl])


def freeze(obj: Class) -> Class:
    def throw_immutable(*_):
        raise exceptions.SamariumTypeError("object is immutable")
    obj._setSlice_ = throw_immutable
    obj._setItem_ = throw_immutable
    return obj


def import_module(data: str, ch: CodeHandler):

    @contextmanager
    def silence_stdout():
        stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        yield
        sys.stdout = stdout

    module_import = False
    try:
        name, object_string = data.split(".")
        objects = object_string.split(",")
    except ValueError:
        name = data
        objects = []
        module_import = True
    name = name.strip("_")
    path = sys.argv[1][:sys.argv[1].rfind("/") + 1] or "."

    if f"{name}.sm" not in os.listdir(path):
        if name not in MODULE_NAMES:
            raise exceptions.SamariumImportError(name)
        path = os.path.join(
            os.path.dirname(__file__),
            "modules"
        )

    with silence_stdout():
        imported = run(readfile(f"{path}/{name}.sm"), CodeHandler(globals()))

    if module_import:
        ch.globals.update({f"_{name}_": Module(name, imported.globals)})
    elif objects == ["*"]:
        imported.globals = {
            k: v for k, v in imported.globals.items()
            if not k.startswith("__") and not k[0].isalnum()
        }
        ch.globals.update(imported.globals)
    else:
        for obj in objects:
            ch.globals[obj] = imported.globals[obj]


def print_safe(*args):
    args = [
        assert_smtype(
            lambda: Type(i) if isinstance(i, (type, type(lambda: 0))) else i
        )()
        for i in args
    ]
    types = [type(i) for i in args]
    if any(i in (tuple, type(i for i in [])) for i in types):
        raise exceptions.SamariumSyntaxError(
            "missing brackets"
            if tuple in types else
            "invalid comprehension"
        )
    print(*args)
    if len(args) > 1:
        return Array([*args])
    elif not args or types[0] is Null:
        return Null()
    return args[0]


def random(start: Integer, end: Integer) -> Integer:
    return Integer(
        randbelow(int(end) - int(start) + 1) + int(start)
    )


def readfile(path: str) -> str:
    with open(path) as f:
        return f.read()


def readline(prompt: str = "") -> String:
    return String(input(prompt))


def run(code: str, ch: CodeHandler, debug: bool = False) -> CodeHandler:

    ch = Transpiler(tokenize(code), ch).transpile()
    prefix = [
        "import sys",
        "import os",
        "STDOUT = sys.stdout",
        "sys.stdout = open(os.devnull, 'w')"
    ]
    suffix = [
        "if __name__ == 'samarium':",
        "    sys.stdout = STDOUT",
        "    argv = Array([String(i) for i in sys.argv[1:]])",
        "    try:",
        "        ex = entry(argv)",
        "    except TypeError:",
        "        ex = entry()",
        "    sys.exit(ex.value)"
    ]
    code = "\n".join(prefix + ch.code + suffix)
    try:
        if debug:
            for line in code.splitlines():
                print(line)
        Runtime.import_level += 1
        ch.globals = {**globals(), **ch.globals}
        exec(code, ch.globals)
        Runtime.import_level -= 1
    except Exception as e:
        exceptions.handle_exception(e)
    return ch


def sleep(time: int):
    _sleep(time / 1000)


def throw(message: str = ""):
    raise exceptions.SamariumError(message)


def verify_mutable(string: str):
    if string in Runtime.frozen:
        raise exceptions.SamariumTypeError("object is immutable")
