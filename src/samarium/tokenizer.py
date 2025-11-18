from __future__ import annotations

import re
import sys
from typing import cast

from crossandra import Crossandra, CrossandraError, Rule, common

from samarium.exceptions import SamariumSyntaxError, handle_exception
from samarium.tokens import Token


def to_number(string: str) -> tuple[int, int] | int:
    string = string.replace("/", "1").replace("\\", "0")
    if "`" in string:
        dec, _, frac = string.partition("`")
        return int(dec or "0", 2), int(frac or "0", 2)
    else:
        return int(string, 2)


Tokenlike = Token | str | int | tuple[int, int]

SM_BIT = r"[\\\/]"

crossandra = Crossandra(
    Token,
    ignore_whitespace=True,
    rules=[
        Rule(r"==<.*>==", flags=re.M | re.S, ignore=True),
        Rule(r"==[^\n]*", flags=re.M | re.S, ignore=True),
        Rule(
            common.DOUBLE_QUOTED_STRING.pattern,
            lambda x: x.replace("\n", r"\n"),
            flags=re.S,
        ),
        Rule(rf"{SM_BIT}+`?{SM_BIT}*|`{SM_BIT}*", to_number),
        Rule(r"[a-zA-Z0-9_]+"),
    ],
)


def tokenize(code: str, *, repl: bool = False) -> list[Tokenlike]:
    try:
        return cast(list[Tokenlike], crossandra.tokenize(code))
    except CrossandraError as e:
        if repl:
            raise
        errmsg = str(e)
        if '"' in errmsg:
            errmsg = "unclosed string literal"
        handle_exception(SamariumSyntaxError(errmsg))
        sys.exit()
