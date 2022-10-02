from pathlib import Path
import sys
from datetime import datetime
from time import sleep as _sleep
from time import time_ns
from types import GeneratorType
from typing import Any

from dahlia import dahlia

from . import exceptions as exc
from .classes import (
    MISSING,
    NULL,
    Array,
    Enum,
    Integer,
    Module,
    Null,
    String,
    Table,
    UserAttrs,
    function,
    mkslice,
    t,
    check_type,
    correct_type,
)
from .runtime import Runtime
from .tokenizer import tokenize
from .transpiler import Registry, Transpiler
from .utils import silence_stdout

MODULE_NAMES = [
    "collections",
    "datetime",
    "io",
    "iter",
    "math",
    "operator",
    "random",
    "string",
    "types",
]


def dtnow() -> Array:
    utcnow = datetime.utcnow()
    now = datetime.now().timetuple()
    utcnow_tt = utcnow.timetuple()
    tz = now[3] - utcnow_tt[3], now[4] - utcnow_tt[4]
    utcnow_tpl = utcnow_tt[:-3] + (utcnow.microsecond // 1000,) + tz
    return Array(map(Integer, utcnow_tpl))


def import_module(data: str, reg: Registry) -> None:
    module_import = False
    try:
        name, object_string = data.split(".")
        objects = object_string.split(",")
    except ValueError:
        name = data
        objects = []
        module_import = True
    name = name.removeprefix("sm_")
    if name == "samarium":
        sys.stderr.write(dahlia("&4[RecursionError]\n"))
        return
    try:
        path = Path(sys.argv[1][: sys.argv[1].rfind("/") + 1] or ".")
    except IndexError:  # REPL
        path = Path().absolute()

    if f"{name}.sm" not in [e.name for e in path.iterdir()]:
        if name not in MODULE_NAMES:
            raise exc.SamariumImportError(f"invalid module: {name}")
        path = Path(__file__).absolute().parent / "modules"

    with silence_stdout():
        imported = run((path / f"{name}.sm").read_text(), Registry(globals()))

    if module_import:
        reg.vars.update({f"sm_{name}": Module(name, imported.vars)})
    elif objects == ["*"]:
        imported.vars = {k: v for k, v in imported.vars.items() if k.startswith("sm_")}
        reg.vars.update(imported.vars)
    else:
        for obj in objects:
            try:
                reg.vars[obj] = imported.vars[obj]
            except KeyError:
                raise exc.SamariumImportError(
                    f"{obj.removeprefix('sm_')} is not a member of the {name} module"
                )


def print_safe(*args) -> Any:
    args = list(map(correct_type, args))
    return_args = args[:]
    args = list(map(str, args))
    types = [*map(type, args)]
    if tuple in types:
        raise exc.SamariumSyntaxError("missing brackets")
    if GeneratorType in types:
        raise exc.SamariumSyntaxError("invalid comprehension")
    print(*args)
    if len(return_args) > 1:
        return Array(return_args)
    elif not return_args or types[0] is Null:
        return NULL
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
        code = (Path(__file__).resolve().parent / "template.py").read_text().replace(
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


def sleep(*args: Integer) -> None:
    if not args:
        raise exc.SamariumTypeError("no argument provided for ,.,")
    if len(args) > 1:
        raise exc.SamariumTypeError(",., only takes one argument")
    (time,) = args
    if not isinstance(time.val, int):
        raise exc.SamariumTypeError(",., only accepts integers")
    _sleep(time.val / 1000)


def throw(message: str = "") -> None:
    raise exc.SamariumError(message)


def timestamp() -> Integer:
    return Integer(time_ns() // 1_000_000)
