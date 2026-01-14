from __future__ import annotations

from enum import Enum
from types import SimpleNamespace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self


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
    XOR = "^^"  # TODO(trag1c): Implement in ≤2025 (optional)

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
    DATACLASS = "@!"
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

    # Literals (only used by the parser, excluded from the tokenization process)
    IDENTIFIER = "IDN"
    STRING = "STR"
    INT = "INT"
    FLOAT = "FLT"

    def __init__(self, lexeme: str) -> None:
        self.index = len(type(self)) + 1

    def __eq__(self, value: object, /) -> bool:
        return self.index == value

    def __hash__(self) -> int:
        return self.index
        return hash((self.name, self.index))

    @classmethod
    def without_literals(cls) -> SimpleNamespace:
        tokens = [t for t in cls if t.index <= 80]
        # The tokenizer only reads __members__
        return SimpleNamespace(__members__=tokens)

    @classmethod
    def from_index(cls, index: int) -> Self:
        return list(cls)[index - 1]


FILE_IO_TOKENS = [t for t in Token if t.name.startswith("FILE_")]

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
