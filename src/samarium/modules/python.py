from __future__ import annotations
from typing import Any
from importlib import import_module


from samarium.classes.base import Attrs, UserAttrs
from samarium.python import export, to_python, to_samarium, SmProxy


Proxy = export(SmProxy)


to_python = export(to_python)
to_samarium = export(to_samarium)


def _import(mod: String):
    return SmProxy(import_module(mod.val))


globals()["import"] = export(_import)
