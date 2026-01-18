from __future__ import annotations

import re
import pytest

from samarium import nodes as n
from samarium.parser import ParseError, Parser

NULL = n.UnitExpr.NULL
INULL = n.UnitExpr.IMPLICIT_NULL


@pytest.mark.parametrize(
    ("source", "statements"),
    [
        (";;", [n.ExprStmt(INULL)] * 2),
        ("!!!", [n.Throw(INULL)]),
        ("!!!();();", [n.Throw(INULL), n.ExprStmt(NULL), n.ExprStmt(NULL)]),
        ("!!!;();", [n.Throw(INULL), n.ExprStmt(NULL)]),
    ],
)
def test_parse_expr_or_throw_stmt(source: str, statements: list[n.Statement]) -> None:
    assert Parser(source).parse() == statements


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("hey", "expected `;` after the expression"),
        ("<>", "unexpected token `<>`")
    ],
)
def test_parse_expr_or_throw_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = Parser(source).parse()


@pytest.mark.parametrize(
    ("source", "statement"),
    [
        ("<=0;", n.Import(n.Identifier("0"), None)),
        ("<=0.*;", n.Import(n.Identifier("0"), "*")),
        (
            "<=0.1;",
            n.Import(n.Identifier("0"), [n.ImportItem(n.Identifier("1"), None)]),
        ),
        ("<=0.[];", n.Import(n.Identifier("0"), [])),
        (
            "<=0.[1, 2];",
            n.Import(
                n.Identifier("0"),
                [
                    n.ImportItem(n.Identifier("1"), None),
                    n.ImportItem(n.Identifier("2"), None),
                ],
            ),
        ),
        (
            "<=0.[1 -> 2];",
            n.Import(
                n.Identifier("0"), [n.ImportItem(n.Identifier("1"), n.Identifier("2"))]
            ),
        ),
    ],
)
def test_parse_import_stmt(source: str, statement: n.Import) -> None:
    assert Parser(source).parse() == [statement]


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("<=;", "expected identifier after `<=`"),
        ("<=5<=", "expected `.` or `;` after module name"),
        ("<=0.*:", "expected `;` after `*`"),
        ("<=0.1", "expected `;` after import item"),
        ("<=0./", "expected import item or array of import items"),
        ("<=0.[]", "expected `;` after import item array"),
        ("<=0.[1 -> 2 3];", "expected `,` between import items"),
        ("<=0.[1 -> 2, /];", "expected import item"),
        ("<=0.[1 ->];", "expected alias name after `->`"),
    ],
)
def test_parse_import_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = Parser(source).parse()


def test_parse_default_stmt() -> None:
    assert Parser("0<>;").parse() == [n.Default(n.Identifier("0"), INULL)]


def test_parse_default_stmt_fail() -> None:
    with pytest.raises(ParseError, match="expected `;` after default value"):
        _ = Parser("0<>").parse()


@pytest.mark.parametrize(
    ("source", "enum"),
    [
        ("0 # {}", n.EnumDef(n.Identifier("0"), [])),
        (
            "0 # { a; }",
            n.EnumDef(n.Identifier("0"), [n.EnumMember(n.Identifier("a"), None)]),
        ),
        (
            "0 # { a: /; }",
            n.EnumDef(n.Identifier("0"), [n.EnumMember(n.Identifier("a"), n.Int(1))]),
        ),
    ],
)
def test_parse_enum_stmt(source: str, enum: n.EnumDef) -> None:
    assert Parser(source).parse() == [enum]


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("0 #;", "expected block after `#`"),
        ("0 # { / }", "expected enum member name"),
        ("0 # { a }", "expected `:` or `;` after enum member name"),
        ("0 # { a: / }", "expected `;` after enum member value"),
    ],
)
def test_parse_enum_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = Parser(source).parse()


def test_parse_file_io_stmt_create() -> None:
    assert Parser("?~>;").parse() == [n.FileIO(NULL, None, INULL)]


@pytest.mark.parametrize(
    ("op", "io_access", "io_binary", "io_quick"),
    [
        ("&~~>", "APPEND", False, False),
        ("<~~", "READ", False, False),
        ("~~>", "WRITE", False, False),
        ("<~>", "READ_WRITE", False, False),
        ("&%~>", "APPEND", True, False),
        ("<~%", "READ", True, False),
        ("%~>", "WRITE", True, False),
        ("<%>", "READ_WRITE", True, False),
        ("&~>", "APPEND", False, True),
        ("<~", "READ", False, True),
        ("~>", "WRITE", False, True),
        ("&%>", "APPEND", True, True),
        ("<%", "READ", True, True),
        ("%>", "WRITE", True, True),
    ],
)
def test_parse_file_io_stmt_access(
    op: str, io_access: str, io_binary: bool, io_quick: bool
) -> None:
    assert Parser(f"a {op} b;").parse() == [
        n.FileIO(
            n.Identifier("a"),
            n.FileIOKind(n.FileIOAccess[io_access], io_binary, io_quick),
            n.Identifier("b"),
        )
    ]


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("?~>", "expected `;` after file path"),
        ("~>", "expected `;` after file I/O statement"),
        ("a ?~> b;", "`?~>` cannot follow an expression"),
    ],
)
def test_parse_file_io_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = Parser(source).parse()


@pytest.mark.parametrize(
    ("source", "targets", "kind"),
    [
        ("x:;", [("x", None)], n.AssignmentKind.REGULAR),
        ("a,b+:;", [("a", None), ("b", None)], n.AssignmentKind.ADD),
        (
            "a<<>>,b,c<</..>>,d^:;",
            [
                ("a", n.Slice(NULL, NULL, NULL)),
                ("b", None),
                ("c", n.Slice(n.Int(1), NULL, NULL)),
                ("d", None),
            ],
            n.AssignmentKind.BXOR,
        ),
    ],
)
def test_parse_assignment_stmt(
    source: str, targets: list[tuple[str, n.Slice | None]], kind: n.AssignmentKind
) -> None:
    assignment_targets = [
        n.AssignmentTarget(n.Identifier(name), slice) for name, slice in targets
    ]
    assert Parser(source).parse() == [n.Assignment(assignment_targets, kind, INULL)]


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("x ~ : 5;", "invalid assignment operator `~:`"),
        ("0:", "expected `;` after assignment statement"),
    ],
)
def test_parse_assignment_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = Parser(source).parse()


@pytest.mark.parametrize("ending", [";", ""])
def test_parse_yield_stmt_ending(ending: str) -> None:
    assert Parser(f".. {{ ** x{ending} }}").parse() == [
        n.While(INULL, n.Block([n.Yield(n.Identifier("x"))]))
    ]


def test_parse_yield_stmt_fail() -> None:
    with pytest.raises(
        ParseError, match="expected `;` or block end after yield statement"
    ):
        _ = Parser("** x").parse()


@pytest.mark.parametrize("ending", [";", ""])
def test_parse_return_stmt_ending(ending: str) -> None:
    assert Parser(f".. {{ * x{ending} }}").parse() == [
        n.While(INULL, n.Block([n.Return(n.Identifier("x"))]))
    ]


def test_parse_return_stmt_fail() -> None:
    with pytest.raises(
        ParseError, match="expected `;` or block end after return statement"
    ):
        _ = Parser("* x").parse()


@pytest.mark.parametrize(
    ("source", "condition", "msg"),
    [
        ("!!;", INULL, None),
    ],
)
def test_parse_assert_stmt(source: str, condition: n.Expr, msg: n.Expr | None) -> None:
    assert Parser(source).parse() == [n.Assert(condition, msg)]


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("!!", "expected `,` or `;` after assert expression"),
        ("!!,", "expected `;` after assert message"),
    ],
)
def test_parse_assert_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = Parser(source).parse()


def test_parse_sleep_stmt() -> None:
    assert Parser(",.,;").parse() == [n.Sleep(INULL)]


def test_parse_sleep_stmt_fail() -> None:
    with pytest.raises(ParseError, match="expected `;` after sleep statement"):
        _ = Parser(",.,").parse()


def test_parse_exit_stmt() -> None:
    assert Parser("=>!;").parse() == [n.Exit(INULL)]


def test_parse_exit_stmt_fail() -> None:
    with pytest.raises(ParseError, match="expected `;` after exit statement"):
        _ = Parser("=>!").parse()


@pytest.mark.parametrize("ending", [";", ""])
def test_parse_break_stmt_ending(ending: str) -> None:
    assert Parser(f".. {{ <-{ending} }}").parse() == [
        n.While(INULL, n.Block([n.UnitStmt.BREAK]))
    ]


@pytest.mark.parametrize("ending", [";", ""])
def test_parse_continue_stmt_ending(ending: str) -> None:
    assert Parser(f".. {{ ->{ending} }}").parse() == [
        n.While(INULL, n.Block([n.UnitStmt.CONTINUE]))
    ]
