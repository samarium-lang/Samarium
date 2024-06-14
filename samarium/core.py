# ruff: noqa: F401
from __future__ import annotations

import ast
import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from samarium import exceptions as exc
from samarium.builtins import (
    dtnow,
    mkslice,
    print_safe,
    readline,
    sleep,
    t,
    throw,
    timestamp,
)
from samarium.classes import (
    MISSING,
    NEXT,
    NULL,
    Array,
    Dataclass,
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
    correct_type,
)
from samarium.exceptions import DAHLIA
from samarium.imports import merge_objects, parse_string, resolve_path
from samarium.runtime import Runtime
from samarium.tokenizer import tokenize
from samarium.transpiler import Registry, Transpiler
from samarium.utils import sysexit

if TYPE_CHECKING:
    from samarium.classes import Attrs


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
            spec = importlib.util.spec_from_file_location(
                mod.name, str(path / f"{mod.name}.py")
            )
            if spec is None:
                msg = "couldn't load spec"
                raise ValueError(msg)
            module = importlib.util.module_from_spec(spec)
            sys.modules[mod.name] = module
            if spec.loader is None:
                msg = "ModuleSpec.loader is None"
                raise ValueError(msg)
            spec.loader.exec_module(module)
            registry = {
                f"sm_{k}": v
                for k, v in vars(module).items()
                if getattr(v, "__pyexported__", False)
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
    repl: bool = False,
) -> Registry:
    runtime_state = Runtime.repl
    Runtime.repl = repl
    code = Transpiler(tokenize(code), reg).transpile().output
    if load_template:
        code = (
            (Path(__file__).resolve().parent / "template.txt")
            .read_text()
            .replace("{{CODE}}", code)
            .replace(
                "{{SOURCE}}",
                str(Path(source).resolve() if isinstance(source, str) else source),
            )
        )
    try:
        if debug:
            code = ast.unparse(ast.parse(code))
            DAHLIA.print(f"&j{code}", file=sys.stderr)
        reg.vars = globals() | reg.vars
        if repl:
            try:
                res = eval(code, reg.vars)
                if not (res is None or res is NULL):
                    print(repr(res))
            except SyntaxError:
                exec(code, reg.vars)
        else:
            exec(code, reg.vars)
    except Exception as e:  # noqa: BLE001
        exc.handle_exception(e)
    Runtime.repl = runtime_state
    return reg
