import exceptions
import objects
import os
import sys
from contextlib import contextmanager
from transpiler import Transpiler, CodeHandler
from secrets import randbelow
from tokenizer import tokenize
from typing import Callable, Union

Castable = Union[objects.Integer, objects.String]
MODULE_NAMES = ["math", "random", "iter", "collections", "types", "string"]


class ImportLevel:
    il = 0


def cast_type(obj: Castable) -> Castable:
    if isinstance(obj, objects.String):
        return objects.Integer(ord(str(obj)))
    elif isinstance(obj, objects.Integer):
        return objects.String(chr(int(obj)))
    else:
        raise exceptions.SamariumTypeError(type(obj).__name__)


def assert_smtype(function: Callable):
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        if isinstance(result, objects.Class):
            return result
        elif isinstance(result, tuple):
            return objects.Array([*result])
        elif isinstance(result, type(None)):
            return objects.Null()
        else:
            raise exceptions.SamariumTypeError(
                f"Invalid return type: {type(result).__name__}"
            )
    return wrapper


def get_type(obj: objects.Class) -> objects.String:
    return objects.String(obj.__class__.__name__)


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
    path = sys.argv[1][:sys.argv[1].rfind("/") + 1]

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


def random(start: objects.Integer, end: objects.Integer) -> objects.Integer:
    return objects.Integer(
        randbelow(int(end) - int(start) + 1) + int(start)
    )


def readfile(path: str) -> str:
    with open(path) as f:
        return f.read()


def readline(prompt: str = ""):
    in_ = input(prompt)
    if set(in_) == {"/", "\\"}:
        return objects.Integer(int(
            in_.replace("/", "1")
            .replace("\\", "0"), 2
        ))
    elif in_.isdigit():
        return objects.Integer(int(in_))
    else:
        return objects.String(in_)


def run(code: str, ch: CodeHandler) -> CodeHandler:

    tokens = tokenize(code)
    transpiler = Transpiler(tokens, ch)
    transpiler.transpile()
    ch = transpiler.ch
    prefix = [
        "import sys",
        "import os",
        "STDOUT = sys.stdout",
        "sys.stdout = open(os.devnull, 'w')"
    ]
    suffix = [
        "if __name__ == '__main__':",
        "    sys.stdout = STDOUT",
        "    entry()"
    ]
    code = "\n".join(prefix + ch.code + suffix)
    try:
        if "--debug" in sys.argv:
            for i, line in enumerate(code.splitlines()):
                print(f"{i+1:^4}" * ("--showlines" in sys.argv) + line)
        ImportLevel.il += 1
        ch.globals = {**globals(), **ch.globals}
        exec(code, ch.globals)
        ImportLevel.il -= 1
    except Exception as e:
        exceptions.handle_exception(e)
    return ch


def throw(message: str = ""):
    raise exceptions.SamariumError(message)
