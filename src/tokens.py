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

    IF = "."
    ELSE = ",,"
    WHILE = ".."
    FOR = "..."

    FUNCTION = "*"
    CLASS = "@"

    STDIN = "?"
    STDOUT = "!"

    AND = "&&"
    OR = "||"
    NOT = "~~"
    BINAND = "&"
    BINOR = "|"
    BINNOT = "~"
    XOR = "^"

    BRACE_OPEN = "{"
    BRACE_CLOSE = "}"

    TRY = "??"
    CATCH = "!!"
    THROW = "!!!"

    STRING = '"'
    IMPORT = "$"
    LAMBDA = "#"
    END = ";"
    INSTANCE = "'"
    DECORATOR = "%"
    SEP = ","
    TO = "->"

    PAREN_OPEN = "("
    PAREN_CLOSE = ")"
