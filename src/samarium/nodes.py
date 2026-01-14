from __future__ import annotations

from enum import Enum, auto
from typing import Literal, NamedTuple, TypeAlias

Primary: TypeAlias = "String | Int | Float | Identifier | UnitExpr | Array | ArrayComp | Table | TableComp | Slice | Index"
Expr: TypeAlias = "Primary | UnaryOp | BinaryOp | IfExpr | Postfix"
SimpleStatement: TypeAlias = "ExprStmt | UnitStmt | Assignment | FileIO | Throw | Exit | Sleep | Assert | Return | Yield | Default | Import"
CompoundStatement: TypeAlias = "If | ForEach | While | Try | FuncDef | ClassDef | DataClassDef | EnumDef"
Statement: TypeAlias = "SimpleStatement | CompoundStatement"
PostfixKind: TypeAlias = "UnitPostfix | Slice | Index | Call | Attribute"


class Identifier(NamedTuple):
    name: str | None
    inst: bool = False
    private: bool = False


class Block(NamedTuple):
    statements: list[Statement]


class UnitStmt(Enum):
    BREAK = auto()
    CONTINUE = auto()


class UnitExpr(Enum):
    NULL = auto()
    TIMESTAMP = auto()
    DATETIME = auto()


class Exit(NamedTuple):
    code: Expr


class Sleep(NamedTuple):
    duration: Expr


class Assert(NamedTuple):
    condition: Expr
    error_message: Expr | None


class If(NamedTuple):
    condition: Expr
    then: Block
    else_: If | Block | None


class ForEach(NamedTuple):
    members: list[Identifier]
    iterable: Expr
    body: Block


class Array(NamedTuple):
    elements: list[Expr]


class ArrayComp(NamedTuple):
    iterable: Expr
    members: list[Identifier]
    body: Expr
    condition: Expr | None


class Table(NamedTuple):
    elements: list[tuple[Expr, Expr]]


class TableComp(NamedTuple):
    iterable: Expr
    members: list[Identifier]
    body: tuple[Expr, Expr]
    condition: Expr | None


class Index(NamedTuple):
    value: Expr


class Slice(NamedTuple):
    start: Expr
    end: Expr
    step: Expr


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


class FuncDef(NamedTuple):
    name: Identifier | FuncSpecialName
    params: list[FuncParam]
    static: bool
    body: Block
    decorators: list[Expr]


class ClassDef(NamedTuple):
    name: Identifier | Literal[FuncSpecialName.ENTRY]
    parents: list[Identifier]
    body: Block


class DataClassDef(NamedTuple):
    name: Identifier
    members: list[Identifier]
    body: Block | None


class EnumMember(NamedTuple):
    name: Identifier
    value: Expr | None


class EnumDef(NamedTuple):
    name: Identifier
    members: list[EnumMember]


class Default(NamedTuple):
    name: Identifier
    value: Expr


class ImportItem(NamedTuple):
    name: Identifier
    alias: Identifier | None


class Import(NamedTuple):
    module: Identifier
    items: list[ImportItem] | Literal["*"] | None


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
    AND = auto()
    IN = auto()
    OR = auto()
    BAND = auto()
    BOR = auto()
    BXOR = auto()


class BinaryOp(NamedTuple):
    lhs: Expr
    op: BinOp
    rhs: Expr


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


class FileIOKind(NamedTuple):
    access: FileIOAccess
    binary: bool
    quick: bool


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
