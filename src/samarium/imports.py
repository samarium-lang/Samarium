from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from re import Pattern, compile, sub
from typing import TYPE_CHECKING

from .classes import Attrs, Module
from .exceptions import SamariumImportError, SamariumSyntaxError

if TYPE_CHECKING:
    from .transpiler import Registry


FORMATTERS = {
    r"\bsm_(\w+)\b": r"\g<1>",
    r"\.?Array\(\[": ".[",
    r"\]\)": "]",
}

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


def parse_string(string: str) -> list[Mod]:
    string = format_string(string)
    for it in Import.__members__.values():
        imptype, pattern = it, it.value
        if pattern.match(string):
            break
    else:
        raise SamariumSyntaxError("invalid import syntax")
    if imptype is Import.MODULE:
        mods = string.split(",")
        out = []
        for m in mods:
            name, _, alias = m.partition(":")
            out.append(Mod(name, alias or None))
        return out
    if imptype is Import.STAR:
        return [Mod(string.split(".")[0], None, objects=True)]
    if imptype is Import.OBJECT:
        mod, obj = string.split(".")
        obj, _, alias = obj.partition(":")
        return [Mod(mod, None, [Obj(obj, alias or None)])]
    mod, objects_ = string.split(".")
    objects = objects_.strip("[]").split(",")
    objs = []
    for o in objects:
        name, _, alias = o.partition(":")
        objs.append(Obj(name, alias or None))
    return [Mod(mod, None, objs)]


def format_string(string: str) -> str:
    for pattern, repl in FORMATTERS.items():
        string = sub(pattern, repl, string)
    return string


def merge_objects(reg: Registry, imported: Registry, module: Mod) -> dict[str, Attrs]:
    vars_ = reg.vars.copy()
    if module.objects is False:
        return vars_ | {f"sm_{module.alias}": Module(module.name, imported.vars)}
    if module.objects is True:
        return vars_ | {k: v for k, v in imported.vars.items() if k.startswith("sm_")}
    for obj in module.objects:
        try:
            vars_[f"sm_{obj.alias}"] = imported.vars[f"sm_{obj.name}"]
        except KeyError:
            raise SamariumImportError(
                f"{obj.name} is not a member of the {module.name} module"
            ) from None
    return vars_


def regex(string: str) -> Pattern:
    return compile("^" + string.replace("W", r"\w+") + "$")


def resolve_path(name: str, source: str) -> Path:
    try:
        path = Path(source).parent
    except IndexError:  # REPL
        path = Path().resolve()
    paths = [e.name for e in path.iterdir()]
    if not (f"{name}.sm" in paths or f"{name}.py" in paths):
        if name not in MODULE_NAMES:
            raise SamariumImportError(f"invalid module: {name}")
        path = Path(__file__).resolve().parent / "modules"
    return path


class Import(Enum):
    MODULE = regex(r"W(?::W)?(?:,W(?::W)?)*")
    STAR = regex(r"W\.\*")
    OBJECT = regex(r"W\.W(?::W)?")
    OBJECTS = regex(r"W\.\[W(?::W)?(?:,W(?::W)?)*\]")


class ImportAttrs:
    name: str
    alias: str | None

    def __post_init__(self) -> None:
        if self.alias is None:
            self.alias = self.name


@dataclass
class Mod(ImportAttrs):
    name: str
    alias: str | None = None
    objects: list[Obj] | bool = False


@dataclass
class Obj(ImportAttrs):
    name: str
    alias: str | None = None
