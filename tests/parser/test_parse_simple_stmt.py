import pytest

from samarium import nodes as n
from samarium.parser import Parser

NULL = n.UnitExpr.NULL
INULL = n.UnitExpr.IMPLICIT_NULL


@pytest.mark.parametrize(
    ("source", "statements"),
    [
        (";;", [n.ExprStmt(INULL)] * 2),
        ("!!!", [n.Throw(INULL)]),
        ("!!!();();", [n.Throw(INULL), n.ExprStmt(NULL), n.ExprStmt(NULL)]),
        ("!!!;();", [n.Throw(INULL), n.ExprStmt(NULL)]),
    ]
)
def test_parse_expr_or_throw_stmt(source: str, statements: list[n.Statement]) -> None:
    assert Parser(source).parse() == statements
