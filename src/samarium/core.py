import os
import sys

from datetime import datetime
from termcolor import colored
from time import sleep as _sleep

from . import exceptions as exc
from .objects import (
    assert_smtype,
    class_attributes,
    smhash,
    verify_type,
    Class,
    Type,
    Slice,
    Null,
    String,
    Integer,
    Module,
    Table,
    Array,
    Enum,
    Mode,
    FileManager,
    File,
)
from .runtime import Runtime
from .tokenizer import tokenize
from .transpiler import Transpiler, CodeHandler
from .utils import readfile, silence_stdout, sysexit

MODULE_NAMES = [
    "collections",
    "datetime",
    "iter",
    "math",
    "operator",
    "random",
    "string",
    "terminal",
    "types",
    "utils",
]


class MISSING:
    def __getattr__(self, _):
        raise exc.SamariumValueError("cannot use the MISSING object")


def dtnow() -> Array:
    utcnow = datetime.utcnow()
    now = [*datetime.now().timetuple()]
    utcnow_tl = [*datetime.utcnow().timetuple()]
    tz = [now[3] - utcnow_tl[3], now[4] - utcnow_tl[4]]
    utcnow_tl = utcnow_tl[:-3] + [utcnow.microsecond // 1000] + tz
    return Array([Integer(i) for i in utcnow_tl])


def import_module(data: str, ch: CodeHandler):

    module_import = False
    try:
        name, object_string = data.split(".")
        objects = object_string.split(",")
    except ValueError:
        name = data
        objects = []
        module_import = True
    name = name.strip("_")
    if name == "samarium":
        sys.stderr.write(colored("[RecursionError]\n"))
        return
    try:
        path = sys.argv[1][: sys.argv[1].rfind("/") + 1] or "."
    except IndexError:  # Shell
        path = os.getcwd() + "/"

    if f"{name}.sm" not in os.listdir(path):
        if name not in MODULE_NAMES:
            raise exc.SamariumImportError(name)
        path = os.path.join(os.path.dirname(__file__), "modules")

    with silence_stdout():
        imported = run(readfile(f"{path}/{name}.sm"), CodeHandler(globals()))

    if module_import:
        ch.globals.update({f"_{name}_": Module(name, imported.globals)})
    elif objects == ["*"]:
        imported.globals = {
            k: v
            for k, v in imported.globals.items()
            if not k.startswith("__") and not k[0].isalnum()
        }
        ch.globals.update(imported.globals)
    else:
        for obj in objects:
            ch.globals[obj] = imported.globals[obj]


def print_safe(*args):
    args = [*map(verify_type, args)]
    return_args = args[:]
    args = [*map(str, args)]
    types = [type(i) for i in args]
    if any(i in (tuple, type(i for i in [])) for i in types):
        raise exc.SamariumSyntaxError(
            "missing brackets" if tuple in types else "invalid comprehension"
        )
    print(*args)
    if len(return_args) > 1:
        return Array([*return_args])
    elif not return_args or types[0] is Null:
        return Null()
    return return_args[0]


def readline(prompt: str = "") -> String:
    return String(input(prompt))


def run(
    code: str,
    ch: CodeHandler,
    debug: bool = False,
    *,
    load_template: bool = True,
    quit_on_error: bool = True,
) -> CodeHandler:

    Runtime.quit_on_error = quit_on_error
    code = "\n".join(Transpiler(tokenize(code), ch).transpile().code)
    if load_template:
        code = readfile(f"{os.path.dirname(__file__)}/template.py").replace(
            "{{ CODE }}", code
        )
    try:
        if debug:
            print(code)
        Runtime.import_level += 1
        ch.globals = globals() | ch.globals
        exec(code, ch.globals)
        Runtime.import_level -= 1
    except Exception as e:
        exc.handle_exception(e)
    return ch


def sleep(*args: Integer):
    if not args:
        raise exc.SamariumTypeError("no argument provided for ,.,")
    if len(args) > 1:
        raise exc.SamariumTypeError(",., only takes one argument")
    (time,) = args
    if not isinstance(time.value, int):
        raise exc.SamariumTypeError(",., only accepts integers")
    _sleep(time.value / 1000)


def throw(message: str = ""):
    raise exc.SamariumError(message)
