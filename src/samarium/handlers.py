from .tokens import Token


class Scroller:

    def __init__(self, program: str):
        self.program = program
        self.prev = ""

    @property
    def pointer(self) -> str:
        return self.program[0]

    def next(self, offset: int = 1) -> str:
        return self.program[offset]

    def shift(self, units: int = 1):
        self.prev = self.program[:units][-1]
        self.program = self.program[units:]


def plus(scroller: Scroller) -> Token:
    if scroller.next() == "+":
        return (Token.MUL, Token.POW)[scroller.next(2) == "+"]
    return Token.ADD


def minus(scroller: Scroller) -> Token:
    tokens = {
        ">": (Token.TO, Token.IN)[scroller.next(2) == "?"],
        "-": (Token.DIV, Token.MOD)[scroller.next(2) == "-"]
    }
    return tokens.get(scroller.next(), Token.SUB)


def colon(scroller: Scroller) -> Token:
    if scroller.next() == ":":
        return (Token.EQ, Token.NE)[scroller.next(2) == ":"]
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
        ">": Token.CONST,
        "<": Token.SLICE_OPEN,
        ":": Token.LE,
        "%": Token.FILE_QUICK_BINARY_READ,
        "~": Token.FILE_QUICK_READ
    }
    return tokens.get(scroller.next(), Token.LT)


def greater(scroller: Scroller) -> Token:
    if scroller.program[:3] == ">==":
        return Token.COMMENT_CLOSE
    tokens = {
        ">": Token.SLICE_CLOSE,
        ":": Token.GE
    }
    return tokens.get(scroller.next(), Token.GT)


def equal(scroller: Scroller) -> Token:
    if scroller.next() == "=":
        try:
            return (Token.COMMENT, Token.COMMENT_OPEN)[scroller.next(2) == "<"]
        except IndexError:
            return Token.COMMENT
    if scroller.next() == ">":
        return (Token.MAIN, Token.EXIT)[scroller.next(2) == "!"]
    raise ValueError("invalid token")


def dot(scroller: Scroller) -> Token:
    if scroller.next() == ".":
        return (Token.WHILE, Token.FOR)[scroller.next(2) == "."]
    return Token.ATTRIBUTE


def question(scroller: Scroller) -> Token:
    if scroller.next() == "?":
        return (Token.TRY, Token.STDIN)[scroller.next(2) == "?"]
    elif scroller.next() == "~":
        if scroller.next(2) == ">":
            return Token.FILE_CREATE
    return (Token.IF, Token.TYPE)[scroller.next() == "!"]


def exclamation(scroller: Scroller) -> Token:
    if scroller.next() == "!":
        return (Token.CATCH, Token.THROW)[scroller.next(2) == "!"]
    return (Token.STDOUT, Token.PARENT)[scroller.next() == "?"]


def pipe(scroller: Scroller) -> Token:
    return (Token.BINOR, Token.OR)[scroller.next() == "|"]


def ampersand(scroller: Scroller) -> Token:
    if scroller.program[:4] == "&~~>":
        return Token.FILE_APPEND
    elif scroller.program[:4] == "&%~>":
        return Token.FILE_BINARY_APPEND
    elif scroller.program[:3] == "&~>":
        return Token.FILE_QUICK_APPEND
    elif scroller.program[:3] == "&%>":
        return Token.FILE_QUICK_BINARY_APPEND
    return (Token.BINAND, Token.AND)[scroller.next() == "&"]


def tilde(scroller: Scroller) -> Token:
    if scroller.next() == "~" and scroller.next(2) == ">":
        return Token.FILE_WRITE
    tokens = {
        ">": Token.FILE_QUICK_WRITE,
        "~": Token.NOT
    }
    return tokens.get(scroller.next(), Token.BINNOT)


def caret(scroller: Scroller) -> Token:
    return (Token.XOR, Token.RANDOM)[scroller.next() == "^"]


def comma(scroller: Scroller) -> Token:
    if scroller.program[1:3] == ".,":
        return Token.SLEEP
    return (Token.SEP, Token.ELSE)[scroller.next() == ","]


def open_brace(scroller: Scroller) -> Token:
    return (Token.BRACE_OPEN, Token.TABLE_OPEN)[scroller.next() == "{"]


def close_brace(scroller: Scroller) -> Token:
    try:
        return (Token.BRACE_CLOSE, Token.TABLE_CLOSE)[scroller.next() == "}"]
    except IndexError:
        return Token.BRACE_CLOSE


def hash_(scroller: Scroller) -> Token:
    return (Token.ASSERT, Token.HASH)[scroller.next() == "#"]


def asterisk(scroller: Scroller) -> Token:
    return (Token.FUNCTION, Token.SLICE_STEP)[scroller.next() == "*"]


def percent(scroller: Scroller) -> Token:
    if scroller.next() == ">":
        return Token.FILE_QUICK_BINARY_WRITE
    elif scroller.next() == "~":
        if scroller.next(2) == ">":
            return Token.FILE_BINARY_WRITE
    return Token.CAST


def at(scroller: Scroller) -> Token:
    return (Token.CLASS, Token.DTNOW)[scroller.next() == "@"]
