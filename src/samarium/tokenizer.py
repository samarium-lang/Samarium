from contextlib import suppress
from .exceptions import SamariumSyntaxError, handle_exception
from .tokens import Token
from typing import List, Tuple, Union
from . import handlers
import sys

Tokenlike = Union[Token, str, int]

MULTISEMANTIC = {
    "+": handlers.plus,
    "-": handlers.minus,
    ":": handlers.colon,
    "<": handlers.less,
    ">": handlers.greater,
    "=": handlers.equal,
    ".": handlers.dot,
    "?": handlers.question,
    "!": handlers.exclamation,
    "&": handlers.ampersand,
    "|": handlers.pipe,
    "~": handlers.tilde,
    ",": handlers.comma,
    "{": handlers.open_brace,
    "}": handlers.close_brace,
    "^": handlers.caret,
    "#": handlers.hash_,
    "*": handlers.asterisk,
    "%": handlers.percent,
    "@": handlers.at
}


def tokenize(program: str) -> List[Tokenlike]:

    comment = False
    scroller = handlers.Scroller(exclude_backticks(program))
    string = False
    temp = ""
    tokens: List[Tokenlike] = []

    while scroller.program:

        if comment:
            if scroller.pointer == "\n":
                comment = False
            scroller.shift()

        # String submitting
        elif scroller.pointer == '"' and scroller.prev != "\\":
            if not string and temp:
                tokens.append(temp)
                temp = ""
            temp += '"'
            string = not string
            if not string:
                tokens.append(temp)
                temp = ""
            scroller.shift()

        # String content and name handling
        elif scroller.pointer.isalnum() or string:
            temp += scroller.pointer
            scroller.shift()

        # Namespace submitting
        elif temp and not scroller.pointer.isalnum() and not string:
            tokens.append(temp)
            temp = ""

        # Multisemantic token handling
        elif scroller.pointer in MULTISEMANTIC:
            if not (out := MULTISEMANTIC[scroller.pointer](scroller)):
                handle_exception(
                    SamariumSyntaxError(f"invalid token: {scroller.pointer}")
                )
            if out == Token.COMMENT:
                comment = True
                scroller.shift(2)
                continue
            tokens.append(out)
            scroller.shift(len(out.value))

        # Number handling
        elif scroller.pointer in "/\\":
            number, length = tokenize_number(scroller)
            tokens.append(number)
            scroller.shift(length)

        else:
            with suppress(ValueError):
                tokens.append(Token(scroller.pointer))
            scroller.shift()

    return exclude_comments(tokens)


def tokenize_number(scroller: handlers.Scroller) -> Tuple[int, int]:
    temp = ""
    for char in scroller.program:
        if char not in "/\\":
            break
        temp += char
    temp = temp.replace("/", "1").replace("\\", "0")
    return int(temp, 2), len(temp)


def exclude_backticks(program: str) -> str:
    out = ""
    skip = False
    for i, c in enumerate(program):
        if c == '"' and program[i - 1] != "\\":
            skip = not skip
        if c == "`" and skip or c != "`":
            out += c
    return out


def exclude_comments(tokens: List[Tokenlike]) -> List[Tokenlike]:
    out = []
    ignore = False
    for token in tokens:
        if token == Token.COMMENT_OPEN:
            ignore = True
        elif token == Token.COMMENT_CLOSE:
            ignore = False
        else:
            out += [token] * (not ignore)
    return out


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        for token in tokenize(f.read()):
            print(token)
