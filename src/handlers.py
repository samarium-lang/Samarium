from tokens import Token

program = ""
index = 0


def init(program_: str, index_: int):
    global program, index
    program = program_
    index = index_


def plus() -> Token | None:
    if program[index - 1] == "+":
        return None
    if program[index + 1] != "+":
        return Token.ADD
    if program[index + 2] == "+":
        return Token.POW
    else:
        return Token.MUL


def minus() -> Token | None:
    if program[index - 1] in "<-":
        return None
    if program[index + 1] == ">":
        return Token.TO
    if program[index + 1] != "-":
        return Token.SUB
    if program[index + 2] == "-":
        return Token.MOD
    else:
        return Token.DIV


def colon() -> Token | None:
    if program[index - 1] in "<>:":
        return None
    if program[index + 1] != ":":
        return Token.ASSIGN
    if program[index + 2] == ":":
        return Token.NE
    else:
        return Token.EQ


def less() -> Token | None:
    if program[index - 1] in "=<":
        return None
    if program[index + 1] == "-":
        return Token.FROM
    if program[index + 1] == "<":
        return Token.SHL
    if program[index + 1] == ":":
        return Token.LE
    else:
        return Token.LT


def greater() -> Token | None:
    if program[index - 1] in "->":
        return None
    if program[index + 1] == ">":
        return Token.SHR
    if program[index + 1:index + 3] == "==":
        return Token.COMMENT_CLOSE
    if program[index + 1] == ":":
        return Token.GE
    else:
        return Token.GT


def equal() -> Token | None:
    if program[index - 1] in "=>":
        return None
    if program[index + 1] == "=":
        if program[index + 2] == "<":
            return Token.COMMENT_OPEN
        else:
            return Token.COMMENT


def dot() -> Token | None:
    if program[index - 1] == ".":
        return None
    if program[index + 1] != ".":
        return Token.IF
    if program[index + 2] == ".":
        return Token.FOR
    else:
        return Token.WHILE


def question() -> Token | None:
    if program[index - 1] == "?":
        return None
    if program[index + 1] == "?":
        return Token.TRY
    else:
        return Token.STDIN


def exclamation() -> Token | None:
    if program[index - 1] == "!":
        return None
    if program[index + 1] != "!":
        return Token.STDOUT
    if program[index + 2] == "!":
        return Token.THROW
    else:
        return Token.CATCH


def pipe() -> Token | None:
    if program[index - 1] == "|":
        return None
    if program[index + 1] == "|":
        return Token.OR
    else:
        return Token.BINOR


def ampersand() -> Token | None:
    if program[index - 1] == "&":
        return None
    if program[index + 1] == "&":
        return Token.AND
    else:
        return Token.BINAND


def tilde() -> Token | None:
    if program[index - 1] == "~":
        return None
    if program[index + 1] == "~":
        return Token.NOT
    else:
        return Token.BINNOT


def comma() -> Token | None:
    if program[index - 1] == ",":
        return None
    if program[index + 1] == ",":
        return Token.ELSE
    else:
        return Token.SEP
