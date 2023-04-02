from __future__ import annotations

import re
import sys
from typing import Union, cast

from crossandra import Crossandra, CrossandraError, Rule, common

from .exceptions import SamariumSyntaxError, handle_exception
from .tokens import Token
from .utils import convert_float


def to_number(string: str) -> int | float:
    string = string.replace("/", "1").replace("\\", "0")
    if string == ".":
        string = "0."
    return convert_float(string, base=2, sep="`")


Tokenlike = Union[Token, str, int]

SM_BIT = r"[\\\/]"

crossandra = Crossandra(
    Token,
    ignore_whitespace=True,
    rules=[
        Rule(r"==<.*>==", converter=False, flags=re.M | re.S),
        Rule(r"==[^\n]*", converter=False, flags=re.M | re.S),
        Rule(
            common.DOUBLE_QUOTED_STRING.pattern,
            lambda x: x.replace("\n", r"\n"),
            re.S,
        ),
        Rule(rf"{SM_BIT}+`?{SM_BIT}*|`{SM_BIT}*", to_number),
        Rule(r"\w+"),
    ],
)


def tokenize(code: str) -> list[Tokenlike]:
    try:
        return cast(list[Tokenlike], crossandra.tokenize(code))
    except CrossandraError as e:
        errmsg = str(e)
        if '"' in errmsg:
            errmsg = "unclosed string literal"
        handle_exception(SamariumSyntaxError(errmsg))
        sys.exit()
