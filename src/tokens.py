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

    # Logical and Membership
    AND = "&&"
    OR = "||"
    NOT = "~~"
    IN = "->?"

    # Biwise
    BINAND = "&"
    BINOR = "|"
    BINNOT = "~"
    XOR = "^"

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
    IF = "?"
    ELSE = ",,"
    WHILE = ".."
    FOR = "..."
    TRY = "??"
    CATCH = "!!"
    THROW = "!!!"
    FROM = "<-"
    TO = "->"

    # Comments
    COMMENT = "=="
    COMMENT_OPEN = "==<"
    COMMENT_CLOSE = ">=="

    # OOP / Functions
    FUNCTION = "*"
    CLASS = "@"
    LAMBDA = "#"
    INSTANCE = "'"
    MAIN = "=>"

    # Slicing
    SLICE_OPEN = "<<"
    SLICE_CLOSE = ">>"
    SLICE_STEP = "**"

    # Object Manipulation
    CAST = "%"
    DOLLAR = "$"
    SIZE = ":!:"
    TYPE = "?!"
    HASH = "##"
    STDIN = "???"
    STDOUT = "!"

    # File I/O
    FILE_CREATE = "?~>"
    FILE_READ = "<~~"
    FILE_WRITE = "~~>"
    FILE_READ_WRITE = "<~>"
    FILE_APPEND = "&~~>"
    FILE_BINARY_READ = "<~%"
    FILE_BINARY_WRITE = "%~>"
    FILE_BINARY_READ_WRITE = "<%>"
    FILE_BINARY_APPEND = "&%~>"
    FILE_QUICK_READ = "<~"
    FILE_QUICK_WRITE = "~>"
    FILE_QUICK_APPEND = "&~>"
    FILE_QUICK_BINARY_READ = "<%"
    FILE_QUICK_BINARY_WRITE = "%>"
    FILE_QUICK_BINARY_APPEND = "&%>"

    # Other
    ASSIGN = ":"
    ATTRIBUTE = "."
    END = ";"
    NULL = "_"
    RANDOM = "^^"
    SEP = ","
    STRING = '"'


FILE_IO_TOKENS = [
    token for name, token in Token.__members__.items()
    if name.startswith("FILE_")
]
