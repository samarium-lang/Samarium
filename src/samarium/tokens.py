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
    GE = ">:"
    GT = ">"
    LE = "<:"
    LT = "<"
    EQ = "::"
    NE = ":::"

    # Logical and Membership
    AND = "&&"
    IN = "->?"
    NOT = "~~"
    OR = "||"
    XOR = "^^"  # TODO

    # Bitwise
    BINAND = "&"
    BINNOT = "~"
    BINOR = "|"
    BINXOR = "^"

    # Parens, Brackets and Braces
    BRACKET_OPEN = "["
    BRACKET_CLOSE = "]"

    BRACE_OPEN = "{"
    BRACE_CLOSE = "}"

    PAREN_OPEN = "("
    PAREN_CLOSE = ")"

    TABLE_OPEN = "{{"
    TABLE_CLOSE = "}}"

    # Control Flow
    CATCH = "!!"
    ELSE = ",,"
    FOR = "..."
    FROM = "<-"
    IF = "?"
    THROW = "!!!"
    TO = "->"
    TRY = "??"
    WHILE = ".."

    # Comments
    COMMENT = "=="
    COMMENT_OPEN = "==<"
    COMMENT_CLOSE = ">=="

    # OOP / Functions
    CLASS = "@"
    DEFAULT = "<>"
    FUNCTION = "*"
    INSTANCE = "'"
    MAIN = "=>"

    # Slicing
    SLICE_OPEN = "<<"
    SLICE_CLOSE = ">>"
    SLICE_STEP = "**"

    # Object Manipulation
    CAST = "%"
    DOLLAR = "$"
    EXIT = "=>!"
    HASH = "##"
    PARENT = "!?"
    TYPE = "?!"
    STDIN = "???"
    STDOUT = "!"

    # File I/O
    FILE_CREATE = "?~>"
    FILE_APPEND = "&~~>"
    FILE_READ = "<~~"
    FILE_WRITE = "~~>"
    FILE_READ_WRITE = "<~>"
    FILE_BINARY_APPEND = "&%~>"
    FILE_BINARY_READ = "<~%"
    FILE_BINARY_WRITE = "%~>"
    FILE_BINARY_READ_WRITE = "<%>"
    FILE_QUICK_APPEND = "&~>"
    FILE_QUICK_READ = "<~"
    FILE_QUICK_WRITE = "~>"
    FILE_QUICK_BINARY_APPEND = "&%>"
    FILE_QUICK_BINARY_READ = "<%"
    FILE_QUICK_BINARY_WRITE = "%>"

    # Other
    ASSERT = "#"
    ASSIGN = ":"
    ATTRIBUTE = "."
    DTNOW = "@@"
    END = ";"
    NULL = "_"
    SEP = ","
    SLEEP = ",.,"
    STRING = '"'


FILE_IO_TOKENS = [
    token for name, token in Token.__members__.items() if name.startswith("FILE_")
]

OPEN_TOKENS = [
    Token.BRACKET_OPEN,
    Token.BRACE_OPEN,
    Token.PAREN_OPEN,
    Token.TABLE_OPEN,
    Token.SLICE_OPEN,
]

CLOSE_TOKENS = [
    Token.BRACKET_CLOSE,
    Token.BRACE_CLOSE,
    Token.PAREN_CLOSE,
    Token.TABLE_CLOSE,
    Token.SLICE_CLOSE,
]
