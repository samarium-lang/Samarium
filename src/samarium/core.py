from __future__ import annotations

from pathlib import Path
from sys import argv, stderr

from dahlia import Dahlia

from . import exceptions as exc
from .builtins import (
    correct_type,
    dtnow,
    function,
    mkslice,
    print_safe,
    readline,
    sleep,
    t,
    throw,
    timestamp,
)
from .classes import (
    MISSING,
    NULL,
    Array,
    Attrs,
    Enum,
    FileManager,
    Integer,
    Mode,
    Module,
    Null,
    String,
    Table,
    UserAttrs,
)
from .runtime import Runtime
from .tokenizer import tokenize
from .transpiler import Registry, Transpiler
from .utils import silence_stdout, sysexit

DAHLIA = Dahlia()
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
        stderr.write(DAHLIA.convert("&4[RecursionError]\n"))
        return
    try:
        path = Path(argv[1][: argv[1].rfind("/") + 1] or ".")
    except IndexError:  # REPL
        path = Path().resolve()

    if f"{name}.sm" not in [e.name for e in path.iterdir()]:
        if name not in MODULE_NAMES:
            raise exc.SamariumImportError(f"invalid module: {name}")
        path = Path(__file__).resolve().parent / "modules"

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
        code = (
            (Path(__file__).resolve().parent / "template.py")
            .read_text()
            .replace("{{ CODE }}", code)
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
