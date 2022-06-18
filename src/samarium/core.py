import os
import sys

from datetime import datetime
from termcolor import colored
from time import sleep as _sleep
from types import GeneratorType

from . import exceptions as exc
from .objects import (
    null,
    Int,
    function,
    class_attributes,
    smhash,
    verify_type,
    Class,
    Type,
    Slice,
    String,
    Integer,
    Module,
    Null,
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
    now = datetime.now().timetuple()
    utcnow_tt = utcnow.timetuple()
    tz = now[3] - utcnow_tt[3], now[4] - utcnow_tt[4]
    utcnow_tpl = utcnow_tt[:-3] + (utcnow.microsecond // 1000,) + tz
    return Array(map(Int, utcnow_tpl))


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
        sys.stderr.write(colored("[RecursionError]\n", "red"))
        return
    try:
        path = sys.argv[1][: sys.argv[1].rfind("/") + 1] or "."
    except IndexError:  # REPL
        path = os.getcwd() + "/"

    if f"{name}.sm" not in os.listdir(path):
        if name not in MODULE_NAMES:
            raise exc.SamariumImportError(f"invalid module: {name}")
        path = os.path.join(os.path.dirname(__file__), "modules")

    with silence_stdout():
        imported = run(readfile(f"{path}/{name}.sm"), CodeHandler(globals()))

    if module_import:
        ch.globals.update({f"_{name}_": Module(name, imported.globals)})
    elif objects == ["*"]:
        imported.globals = {
            k: v
            for k, v in imported.globals.items()
            if not (k.startswith("__") or k[0].isalnum())
        }
        ch.globals.update(imported.globals)
    else:
        for obj in objects:
            try:
                ch.globals[obj] = imported.globals[obj]
            except KeyError:
                raise exc.SamariumImportError(
                    f"{obj} is not a member of the {name} module"
                )


def print_safe(*args):
    args = [*map(verify_type, args)]
    return_args = args[:]
    args = [i._toString_() for i in args]
    types = [*map(type, args)]
    if tuple in types:
        raise exc.SamariumSyntaxError("missing brackets")
    if GeneratorType in types:
        raise exc.SamariumSyntaxError("invalid comprehension")
    print(*args)
    if len(return_args) > 1:
        return Array(return_args)
    elif not return_args or types[0] is Null:
        return null
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

    runtime_state = Runtime.quit_on_error
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
    Runtime.quit_on_error = runtime_state
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
