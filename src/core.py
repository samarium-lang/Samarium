import exceptions
import os
import sys
from contextlib import contextmanager
from datetime import datetime
from objects import *
from transpiler import Transpiler, CodeHandler
from secrets import randbelow
from tokenizer import tokenize
from typing import Union

Castable = Union[Integer, String]
MODULE_NAMES = ["math", "random", "iter", "collections", "types", "string"]


class Runtime:
    frozen = []
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
    obj.setSlice_ = throw_immutable
    obj.setItem_ = throw_immutable
    return obj



def import_module(data: str, ch: CodeHandler):

    @contextmanager
    def silence_stdout():
        stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        yield
        sys.stdout = stdout

    name, objects = data.split(".")
    name = name[:-1]
    objects = objects.split(",")
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
    if objects == ["*"]:
        ch.globals.update(imported.globals)
    else:
        for obj in objects:
            ch.globals[obj] = imported.globals[obj]


def print_safe(*args):
    types = [type(i) for i in args]
    if any(i in (tuple, type(i for i in [])) for i in types):
        raise exceptions.SamariumSyntaxError(
            "missing brackets"
            if tuple in types else
            "invalid comprehension"
        )
    print(*args)


def random(start: Integer, end: Integer) -> Integer:
    return Integer(
        randbelow(int(end) - int(start) + 1) + int(start)
    )


def readfile(path: str) -> str:
    with open(path) as f:
        return f.read()


def readline(prompt: str = "") -> String:
    return String(input(prompt))


def run(code: str, ch: CodeHandler) -> CodeHandler:

    tokens = tokenize(code)
    transpiler = Transpiler(tokens, ch)
    ch = transpiler.transpile()
    prefix = [
        "import sys",
        "import os",
        "STDOUT = sys.stdout",
        "sys.stdout = open(os.devnull, 'w')"
    ]
    suffix = [
        "if __name__ == '__main__':",
        "    sys.stdout = STDOUT",
        "    try:"
        "        entry(Array([String(i) for i in sys.argv[1:]]))",
        "    except TypeError:",
        "        entry()"
    ]
    code = "\n".join(prefix + ch.code + suffix)
    try:
        if "--debug" in sys.argv:
            for i, line in enumerate(code.splitlines()):
                print(f"{i+1:^4}" * ("--showlines" in sys.argv) + line)
        Runtime.import_level += 1
        ch.globals = {**globals(), **ch.globals}
        exec(code, ch.globals)
        Runtime.import_level -= 1
    except Exception as e:
        exceptions.handle_exception(e)
    return ch


def throw(message: str = ""):
    raise exceptions.SamariumError(message)


def verify_mutable(string: str):
    if string in Runtime.frozen:
        raise exceptions.SamariumTypeError("object is immutable")
