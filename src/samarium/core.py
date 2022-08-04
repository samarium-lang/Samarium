import os
import sys

from datetime import datetime
from dahlia import dahlia
from time import sleep as _sleep, time_ns
from types import GeneratorType

from . import exceptions as exc
from .objects import (
    null,
    Int,
    function,
    class_attributes,
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
    Enum_,
    Mode,
    FileManager,
    File,
)
from .runtime import Runtime
from .tokenizer import tokenize
from .transpiler import Transpiler, Registry
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


def import_module(data: str, reg: Registry):

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
        sys.stderr.write(dahlia("&4[RecursionError]\n"))
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
        imported = run(readfile(f"{path}/{name}.sm"), Registry(globals()))

    if module_import:
        reg.vars.update({f"_{name}_": Module(name, imported.vars)})
    elif objects == ["*"]:
        imported.vars = {
            k: v
            for k, v in imported.vars.items()
            if not (k.startswith("__") or k[0].isalnum())
        }
        reg.vars.update(imported.vars)
    else:
        for obj in objects:
            try:
                reg.vars[obj] = imported.vars[obj]
            except KeyError:
                raise exc.SamariumImportError(
                    f"{obj} is not a member of the {name} module"
                )


def print_safe(*args):
    args = [*map(verify_type, args)]
    return_args = args[:]
    args = [i.sm_toString() for i in args]
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
    reg: Registry,
    debug: bool = False,
    *,
    load_template: bool = True,
    quit_on_error: bool = True,
) -> Registry:

    runtime_state = Runtime.quit_on_error
    Runtime.quit_on_error = quit_on_error
    code = Transpiler(tokenize(code), reg).transpile().output
    if load_template:
        code = readfile(f"{os.path.dirname(__file__)}/template.py").replace(
            "{{ CODE }}", code
        )
    try:
        if debug:
            print(code)
        Runtime.import_level += 1
        reg.vars = globals() | reg.vars
        exec(code, reg.vars)
        Runtime.import_level -= 1
    except Exception as e:
        exc.handle_exception(e)
    Runtime.quit_on_error = runtime_state
    return reg


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


def timestamp() -> Integer:
    return Int(time_ns() // 1_000_000)
