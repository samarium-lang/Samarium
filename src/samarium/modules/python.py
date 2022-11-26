from __future__ import annotations
from importlib import import_module


from samarium.classes.base import String
from samarium.python import PyProxy, export, to_python, to_samarium, SmProxy, sm_function, py_function


SmProxy = export(SmProxy)
PyProxy = export(PyProxy)

to_python = export(to_python)
to_samarium = export(to_samarium)
sm_function = export(sm_function)
py_function = export(py_function)


def _import(mod: String):
    return SmProxy(import_module(mod.val))


globals()["import"] = export(_import)
