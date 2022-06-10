from .tokens import Token


class Scroller:
    def __init__(self, program: str):
        self.program = program
        self.prev = ""

    @property
    def pointer(self) -> str:
        return self.program[:1]

    def next(self, offset: int = 1) -> str:
        return self.program[offset:offset + 1]

    def shift(self, units: int = 1):
        self.prev = self.program[:units][-1]
        self.program = self.program[units:]


def plus(scroller: Scroller) -> Token:
    if scroller.next() == "+":
        return Token.POW if scroller.next(2) == "+" else Token.MUL
    return Token.ADD


def minus(scroller: Scroller) -> Token:
    tokens = {
        ">": Token.IN if scroller.next(2) == "?" else Token.TO,
        "-": Token.MOD if scroller.next(2) == "-" else Token.DIV,
    }
    return tokens.get(scroller.next(), Token.SUB)


def colon(scroller: Scroller) -> Token:
    if scroller.next() == ":":
        return Token.NE if scroller.next(2) == ":" else Token.EQ
    return Token.ASSIGN


def less(scroller: Scroller) -> Token:
    if scroller.next() == "~":
        if scroller.next(2) == "~":
            return Token.FILE_READ
        elif scroller.next(2) == ">":
            return Token.FILE_READ_WRITE
        elif scroller.next(2) == "%":
            return Token.FILE_BINARY_READ
    elif scroller.next() == "%":
        if scroller.next(2) == ">":
            return Token.FILE_BINARY_READ_WRITE
    tokens = {
        "-": Token.FROM,
        ">": Token.DEFAULT,
        "<": Token.SLICE_OPEN,
        ":": Token.LE,
        "%": Token.FILE_QUICK_BINARY_READ,
        "~": Token.FILE_QUICK_READ,
    }
    return tokens.get(scroller.next(), Token.LT)


def greater(scroller: Scroller) -> Token:
    if scroller.program[:3] == ">==":
        return Token.COMMENT_CLOSE
    tokens = {">": Token.SLICE_CLOSE, ":": Token.GE}
    return tokens.get(scroller.next(), Token.GT)


def equal(scroller: Scroller) -> Token:
    if scroller.next() == "=":
        return Token.COMMENT_OPEN if scroller.next(2) == "<" else Token.COMMENT
    if scroller.next() == ">":
        return Token.EXIT if scroller.next(2) == "!" else Token.MAIN
    raise ValueError("invalid token")


def dot(scroller: Scroller) -> Token:
    if scroller.next() == ".":
        return Token.FOR if scroller.next(2) == "." else Token.WHILE
    return Token.ATTRIBUTE


def question(scroller: Scroller) -> Token:
    if scroller.next() == "?":
        return Token.STDIN if scroller.next(2) == "?" else Token.TRY
    elif scroller.next() == "~":
        if scroller.next(2) == ">":
            return Token.FILE_CREATE
    return Token.TYPE if scroller.next() == "!" else Token.IF


def exclamation(scroller: Scroller) -> Token:
    if scroller.next() == "!":
        return Token.THROW if scroller.next(2) == "!" else Token.CATCH
    return Token.PARENT if scroller.next() == "?" else Token.STDOUT


def pipe(scroller: Scroller) -> Token:
    return Token.OR if scroller.next() == "|" else Token.BINOR


def ampersand(scroller: Scroller) -> Token:
    if scroller.program[:4] == "&~~>":
        return Token.FILE_APPEND
    elif scroller.program[:4] == "&%~>":
        return Token.FILE_BINARY_APPEND
    elif scroller.program[:3] == "&~>":
        return Token.FILE_QUICK_APPEND
    elif scroller.program[:3] == "&%>":
        return Token.FILE_QUICK_BINARY_APPEND
    return Token.AND if scroller.next() == "&" else Token.BINAND


def tilde(scroller: Scroller) -> Token:
    if scroller.next() == "~" and scroller.next(2) == ">":
        return Token.FILE_WRITE
    tokens = {">": Token.FILE_QUICK_WRITE, "~": Token.NOT}
    return tokens.get(scroller.next(), Token.BINNOT)


def caret(scroller: Scroller) -> Token:
    return Token.XOR if scroller.next() == "^" else Token.BINXOR


def comma(scroller: Scroller) -> Token:
    if scroller.program[1:3] == ".,":
        return Token.SLEEP
    return Token.ELSE if scroller.next() == "," else Token.SEP


def open_brace(scroller: Scroller) -> Token:
    return Token.TABLE_OPEN if scroller.next() == "{" else Token.BRACE_OPEN


def close_brace(scroller: Scroller) -> Token:
    return Token.TABLE_CLOSE if scroller.next() == "}" else Token.BRACE_CLOSE


def hash_(scroller: Scroller) -> Token:
    return Token.HASH if scroller.next() == "#" else Token.ASSERT


def asterisk(scroller: Scroller) -> Token:
    return Token.SLICE_STEP if scroller.next() == "*" else Token.FUNCTION


def percent(scroller: Scroller) -> Token:
    if scroller.next() == ">":
        return Token.FILE_QUICK_BINARY_WRITE
    elif scroller.next() == "~":
        if scroller.next(2) == ">":
            return Token.FILE_BINARY_WRITE
    return Token.CAST


def at(scroller: Scroller) -> Token:
    return Token.DTNOW if scroller.next() == "@" else Token.CLASS
