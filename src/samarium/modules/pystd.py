from __future__ import annotations

from samarium.python import export


@export
def round_(x: float, ndigits: int | None = None) -> float:
    return round(x, ndigits)
