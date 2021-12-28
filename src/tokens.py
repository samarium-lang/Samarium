from enum import Enum


class Token(Enum):

    # Arithmetic
    ADD = "+"
    SUB = "-"
    MUL = "++"
    DIV = "--"
    POW = "+++"
    MOD = "---"

    # Comparison
    LT = "<"
    GT = ">"
    LE = "<:"
    GE = ">:"
    EQ = "::"
    NE = ":::"

    # Logical and Bitwise
    AND = "&&"
    OR = "||"
    NOT = "~~"

    BINAND = "&"
    BINOR = "|"
    BINNOT = "~"
    XOR = "^"

    SHR = ">>"
    SHL = "<<"

    # Parens, Brackets and Braces
    ARRAY_OPEN = "["
    ARRAY_CLOSE = "]"

    BRACE_OPEN = "{"
    BRACE_CLOSE = "}"

    PAREN_OPEN = "("
    PAREN_CLOSE = ")"

    TABLE_OPEN = "{{"
    TABLE_CLOSE = "}}"

    # Control Flow
    IF = "?"
    ELSE = ",,"
    WHILE = ".."
    FOR = "..."
    TRY = "??"
    CATCH = "!!"
    THROW = "!!!"

    # Comments
    COMMENT = "=="
    COMMENT_OPEN = "==<"
    COMMENT_CLOSE = ">=="

    # OOP
    FUNCTION = "*"
    CLASS = "@"
    LAMBDA = "#"
    INSTANCE = "'"
    DECORATOR = "%"

    # Other
    ASSIGN = ":"
    ATTRIBUTE = "."
    DOLLAR = "$"
    END = ";"
    FROM = "<-"
    IN = "->?"
    RANDOM = "^^"
    SEP = ","
    STDIN = "???"
    STDOUT = "!"
    STRING = '"'
    TO = "->"
