from __future__ import annotations

from pathlib import Path

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
    NEXT,
    NULL,
    Array,
    Attrs,
    Enum,
    FileManager,
    Integer,
    Int,
    Mode,
    Module,
    Null,
    String,
    Table,
    UserAttrs,
)
from .imports import merge_objects, parse_string, resolve_path
from .runtime import Runtime
from .tokenizer import tokenize
from .transpiler import Registry, Transpiler
from .utils import silence_stdout, sysexit


def import_to_scope(data: str, reg: Registry) -> None:
    modules = parse_string(data)
    for mod in modules:
        if mod.name == "samarium":
            raise exc.SamariumRecursionError
        path = resolve_path(mod.name)
        with silence_stdout():
            imported = run((path / f"{mod.name}.sm").read_text(), Registry({}))
        reg.vars.update(merge_objects(reg, imported, mod))


def import_inline(data: str) -> Attrs:
    reg = Registry({})
    import_to_scope(data, reg)
    return reg.vars.popitem()[1]


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
        reg.vars = globals() | reg.vars
        exec(code, reg.vars)
    except Exception as e:
        exc.handle_exception(e)
    Runtime.quit_on_error = runtime_state
    return reg
