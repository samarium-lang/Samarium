from tokens import Token
from typing import Callable

program = ""
index = 0


def nextchar(offset: int = 1) -> str:
    return program[index + offset]


def init(program_: str, index_: int):
    global program, index
    program = program_
    index = index_


def cancel(chars: str):
    def decorator(function: Callable):
        def wrapper() -> Token | None:
            if program[index - 1] in chars:
                return None
            return function()
        return wrapper
    return decorator


@cancel("+")
def plus() -> Token:
    if nextchar() == "+":
        return (Token.MUL, Token.POW)[nextchar(2) == "+"]
    return Token.ADD


@cancel("<-")
def minus() -> Token:
    match nextchar():
        case ">": return (Token.TO, Token.IN)[nextchar(2) == "?"]
        case "-": return (Token.DIV, Token.MOD)[nextchar(2) == "-"]
        case _: return Token.SUB


@cancel("<>:")
def colon() -> Token:
    if nextchar() == ":":
        return (Token.EQ, Token.NE)[nextchar(2) == ":"]
    return Token.ASSIGN


@cancel("=<")
def less() -> Token:
    match nextchar():
        case "-": return Token.FROM
        case "<": return Token.SHL
        case ":": return Token.LE
        case _: return Token.LT


@cancel("->")
def greater() -> Token:
    if program[index + 1:index + 3] == "==":
        return Token.COMMENT_CLOSE
    match nextchar():
        case ">": return Token.SHR
        case ":": return Token.GE
        case _: return Token.GT


@cancel("=>")
def equal() -> Token:
    if nextchar() == "=":
        return (Token.COMMENT, Token.COMMENT_OPEN)[nextchar(2) == "<"]
    raise ValueError("Invalid token")


@cancel(".")
def dot() -> Token:
    if nextchar() == ".":
        return (Token.WHILE, Token.FOR)[nextchar(2) == "."]
    return Token.ATTRIBUTE


@cancel(">?")
def question() -> Token:
    if nextchar() == "?":
        return (Token.TRY, Token.STDIN)[nextchar(2) == "?"]
    return Token.IF


@cancel("!")
def exclamation() -> Token:
    if nextchar() == "!":
        return (Token.CATCH, Token.THROW)[nextchar(2) == "!"]
    return Token.STDOUT


@cancel("|")
def pipe() -> Token:
    return (Token.BINOR, Token.OR)[nextchar() == "|"]


@cancel("&")
def ampersand() -> Token:
    return (Token.BINAND, Token.AND)[nextchar() == "&"]


@cancel("~")
def tilde() -> Token:
    return (Token.BINNOT, Token.NOT)[nextchar() == "~"]


@cancel("^")
def caret() -> Token:
    return (Token.XOR, Token.RANDOM)[nextchar() == "^"]


@cancel(",")
def comma() -> Token:
    return (Token.SEP, Token.ELSE)[nextchar() == ","]


@cancel("{")
def open_brace() -> Token:
    return (Token.BRACE_OPEN, Token.TABLE_OPEN)[nextchar() == "{"]


@cancel("}")
def close_brace() -> Token:
    try:
        return (Token.BRACE_CLOSE, Token.TABLE_CLOSE)[nextchar() == "}"]
    except IndexError:
        return Token.BRACE_CLOSE
