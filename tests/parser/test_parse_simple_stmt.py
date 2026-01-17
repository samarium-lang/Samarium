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
