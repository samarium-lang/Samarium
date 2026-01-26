from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field
from enum import Enum, auto
from typing import Literal, NamedTuple, TypeAlias

Primary: TypeAlias = "String | Int | Float | Identifier | UnitExpr | Array | ArrayComp | Table | TableComp | Slice | Index"
Expr: TypeAlias = "Primary | UnaryOp | BinaryOp | BinaryLogOp | IfExpr | Postfix"
SimpleStatement: TypeAlias = "ExprStmt | UnitStmt | Assignment | FileIO | Throw | Exit | Sleep | Assert | Return | Yield | Default | Import"
CompoundStatement: TypeAlias = (
    "If | ForEach | While | Try | FuncDef | ClassDef | DataClassDef | EnumDef"
)
Statement: TypeAlias = "SimpleStatement | CompoundStatement"
PostfixKind: TypeAlias = "UnitPostfix | Slice | Index | Call | Attribute"


@dataclass(slots=True)
class Identifier:
    name: str | None
    _: KW_ONLY
    inst: bool = False
    private: bool = False


@dataclass(slots=True)
class Block:
    statements: list[Statement] = field(default_factory=list)


class UnitStmt(Enum):
    BREAK = auto()
    CONTINUE = auto()


class UnitExpr(Enum):
    IMPLICIT_NULL = auto()
    NULL = auto()
    TIMESTAMP = auto()
    DATETIME = auto()


# Very commonly used
INULL = UnitExpr.IMPLICIT_NULL
NULL = UnitExpr.NULL


class Exit(NamedTuple):
    code: Expr


class Sleep(NamedTuple):
    duration: Expr


class Assert(NamedTuple):
    condition: Expr
    error_message: Expr | None = None


class If(NamedTuple):
    condition: Expr
    then: Block
    else_: If | Block | None = None


class ForEach(NamedTuple):
    members: list[Identifier]
    iterable: Expr
    body: Block


@dataclass(slots=True)
class Array:
    elements: list[Expr] = field(default_factory=list)


class ArrayComp(NamedTuple):
    iterable: Expr
    members: list[Identifier]
    body: Expr
    condition: Expr | None = None


@dataclass(slots=True)
class Table:
    elements: list[tuple[Expr, Expr]] = field(default_factory=list)


class TableComp(NamedTuple):
    iterable: Expr
    members: list[Identifier]
    body: tuple[Expr, Expr]
    condition: Expr | None = None


class Index(NamedTuple):
    value: Expr


@dataclass(slots=True, kw_only=True)
class Slice:
    start: Expr | None = None
    stop: Expr | None = None
    step: Expr | None = None


class Call(NamedTuple):
    args: list[Expr]


class While(NamedTuple):
    condition: Expr
    body: Block


class Try(NamedTuple):
    try_: Block
    catch: Block


class Return(NamedTuple):
    expr: Expr


class Yield(NamedTuple):
    expr: Expr


class FuncParamKind(Enum):
    DEFAULT = auto()
    VARIADIC = auto()
    OPTIONAL = auto()


class FuncParam(NamedTuple):
    name: Identifier
    kind: FuncParamKind


class FuncSpecialName(Enum):
    ADD = auto()
    SUB = auto()
    POW = auto()
    MUL = auto()
    MOD = auto()
    DIV = auto()
    IN = auto()
    NE = auto()
    EQ = auto()
    LE = auto()
    GE = auto()
    LT = auto()
    GT = auto()
    HASH = auto()
    FOR = auto()
    TRY = auto()
    IF = auto()
    PRINT = auto()
    BXOR = auto()
    SPECIAL = auto()
    CAST = auto()
    BNOT = auto()
    BOR = auto()
    BAND = auto()
    ZIP = auto()
    ENTRY = auto()
    POS = auto()
    NEG = auto()
    GET = auto()
    SET = auto()


@dataclass(slots=True)
class FuncDef:
    name: Identifier | FuncSpecialName
    params: list[FuncParam]
    static: bool
    body: Block
    decorators: list[Expr] = field(default_factory=list)


class ClassDef(NamedTuple):
    name: Identifier | Literal[FuncSpecialName.ENTRY]
    parents: list[Identifier]
    body: Block


class DataClassDef(NamedTuple):
    name: Identifier
    members: list[Identifier]
    body: Block | None = None


class EnumMember(NamedTuple):
    name: Identifier
    value: Expr | None = None


class EnumDef(NamedTuple):
    name: Identifier
    members: list[EnumMember]


class Default(NamedTuple):
    name: Identifier
    value: Expr


class ImportItem(NamedTuple):
    name: Identifier
    alias: Identifier | None = None


class Import(NamedTuple):
    module: Identifier
    items: list[ImportItem] | Literal["*"] | None = None


class ExprStmt(NamedTuple):
    expr: Expr


class Throw(NamedTuple):
    value: Expr


class IfExpr(NamedTuple):
    condition: Expr
    then: Expr
    else_: Expr


class BinOp(Enum):
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    POW = auto()
    MOD = auto()
    ZIP = auto()
    GE = auto()
    GT = auto()
    LE = auto()
    LT = auto()
    EQ = auto()
    NE = auto()
    IN = auto()
    NIN = auto()
    BAND = auto()
    BOR = auto()
    BXOR = auto()


class BinaryOp(NamedTuple):
    lhs: Expr
    op: BinOp
    rhs: Expr


class LogOp(Enum):
    OR = auto()
    AND = auto()


class BinaryLogOp(NamedTuple):
    lhs: Expr
    rhss: list[tuple[LogOp, Expr]]


class UnOp(Enum):
    ADD = auto()
    SUB = auto()
    FROM = auto()
    NOT = auto()
    BNOT = auto()
    YIELD = auto()


class UnaryOp(NamedTuple):
    ops: list[UnOp]
    expr: Expr


class AssignmentTarget(NamedTuple):
    # TODO: support attribute update
    name: Identifier
    subscript: Index | Slice | Attribute | None


class AssignmentKind(Enum):
    REGULAR = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    POW = auto()
    MOD = auto()
    BOR = auto()
    BAND = auto()
    BXOR = auto()


class Assignment(NamedTuple):
    targets: list[AssignmentTarget]
    kind: AssignmentKind
    value: Expr


class FileIOAccess(Enum):
    APPEND = auto()
    READ = auto()
    WRITE = auto()
    READ_WRITE = auto()


@dataclass(slots=True)
class FileIOKind:
    access: FileIOAccess
    _: KW_ONLY
    binary: bool = False
    quick: bool = False


class FileIO(NamedTuple):
    lhs: Expr
    kind: FileIOKind | None  # None for file creation
    rhs: Expr


class String(NamedTuple):
    value: str


class Int(NamedTuple):
    value: int


class Float(NamedTuple):
    dec: int
    frac: int


class Attribute(NamedTuple):
    name: Identifier


class UnitPostfix(Enum):
    CAST = "CAST"
    HASH = "HASH"
    PRINT = "PRINT"
    PARENT = "PARENT"
    READLINE = "READLINE"
    SPECIAL = "SPECIAL"
    TYPE = "TYPE"
    # Reusing tokens
    ID = "YIELD"
    RANDOM = "TRY"


class Postfix(NamedTuple):
    value: Expr
    kind: PostfixKind
