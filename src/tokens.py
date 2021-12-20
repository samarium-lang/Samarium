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

    ARRAY_OPEN = "["
    ARRAY_CLOSE = "]"

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

    IF = "?"
    ELSE = ",,"
    WHILE = ".."
    FOR = "..."

    FUNCTION = "*"
    CLASS = "@"

    STDIN = "???"
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
    DOLLAR = "$"
    LAMBDA = "#"
    END = ";"
    INSTANCE = "'"
    DECORATOR = "%"
    SEP = ","
    TO = "->"
    FROM = "<-"
    IN = "->?"

    PAREN_OPEN = "("
    PAREN_CLOSE = ")"
