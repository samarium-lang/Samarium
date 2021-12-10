from enum import Enum


class Token(Enum):
    ADD = "+"
    SUB = "-"
    MUL = "++"
    DIV = "--"
    POW = "+++"
    MOD = "---"
    SHR = ">>"
    SHL = "<<"

    VECTOR_OPEN = "["
    VECTOR_CLOSE = "]"

    ASSIGN = ":"

    LT = "<"
    GT = ">"
    LE = "<:"
    GE = ">:"
    EQ = "::"
    NE = ":::"

    COMMENT = "=="
    COMMENT_OPEN = "==<"
    COMMENT_CLOSE = ">=="

    ZERO = "\\"
    ONE = "/"

    IF = "."
    ELSE = ","
    WHILE = ".."
    FOR = "..."

    FUNCTION = "*"
    CLASS = "@"

    STDIN = "?"
    STDOUT = "!"

    AND = "&"
    OR = "|"
    NOT = "~"
    XOR = "^"

    BRACE_OPEN = "{"
    BRACE_CLOSE = "}"

    TRY = "??"
    CATCH = "!!"
    THROW = "!!!"

    STRING = '"'
    DOLLAR = "$"
    CONST = "#"
    LAMBDA = "_"
    END = ";"
    CAST = "'"
    DECORATOR = "%"

    PAREN_OPEN = "("
    PAREN_CLOSE = ")"
