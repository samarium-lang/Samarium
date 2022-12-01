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
    BAND = "&"
    BNOT = "~"
    BOR = "|"
    BXOR = "^"

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
    IMPORT = "<="
    THROW = "!!!"
    TO = "->"
    TRY = "??"
    WHILE = ".."

    # OOP / Functions
    CLASS = "@"
    DEFAULT = "<>"
    FUNCTION = "*"
    INSTANCE = "'"
    ENTRY = "=>"
    YIELD = "**"

    # Slicing
    SLICE_OPEN = "<<"
    SLICE_CLOSE = ">>"

    # Object Manipulation
    CAST = "%"
    SPECIAL = "$"
    EXIT = "=>!"
    HASH = "##"
    PARENT = "!?"
    TYPE = "?!"
    READLINE = "???"
    PRINT = "!"

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
    ENUM = "#"
    ASSIGN = ":"
    ATTR = "."
    UNIX_STMP = "@@"
    ARR_STMP = "@@@"
    END = ";"
    SEP = ","
    SLEEP = ",.,"
    ZIP = "><"


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
