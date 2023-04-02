from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from . import exceptions as exc
from .builtins import (
    correct_type,
    dtnow,
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
    Enum,
    FileManager,
    Function,
    Mode,
    Module,
    Null,
    Num,
    Number,
    String,
    Table,
    UserAttrs,
)
from .imports import merge_objects, parse_string, resolve_path
from .runtime import Runtime
from .tokenizer import tokenize
from .transpiler import Registry, Transpiler
from .utils import sysexit

if TYPE_CHECKING:
    from .classes import Attrs


def import_to_scope(data: str, reg: Registry, source: str) -> None:
    modules = parse_string(data)
    for mod in modules:
        if mod.name == "samarium":
            raise exc.SamariumRecursionError
        path = resolve_path(mod.name, source)
        mod_path = (path / f"{mod.name}.sm").resolve()
        if mod_path.exists():
            imported = run(mod_path.read_text(), Registry({}), mod_path)
        else:
            spec: importlib.machinery.ModuleSpec = (
                importlib.util.spec_from_file_location(
                    mod.name, str(path / f"{mod.name}.py")
                )
            )  # type: ignore
            module = importlib.util.module_from_spec(spec)
            sys.modules[mod.name] = module
            spec.loader.exec_module(module)  # type: ignore
            registry = {
                f"sm_{k}": v
                for k, v in vars(module).items()
                if f"__export_{v}" in dir(v)
            }
            imported = Registry(registry)

        reg.vars.update(merge_objects(reg, imported, mod))


def import_inline(data: str, source: str) -> Attrs:
    reg = Registry({})
    import_to_scope(data, reg, source)
    return reg.vars.popitem()[1]


def run(
    code: str,
    reg: Registry,
    source: Path | str,
    *,
    debug: bool = False,
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
            .replace(
                "{{ SOURCE }}",
                str(Path(source).resolve() if isinstance(source, str) else source),
            )
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
