import pytest

from samarium import nodes as n
from samarium.parser import ParseError, Parser

NULL = n.UnitExpr.NULL
INULL = n.UnitExpr.IMPLICIT_NULL


@pytest.mark.parametrize(
    ("inner_source", "args"),
    [
        ("", []),
        (",", [INULL]),
        ("()", [NULL]),
        ("(), , ,()", [NULL, INULL, INULL, NULL]),
        ("a,b", [n.Identifier("a"), n.Identifier("b")]),
        ("a,b,", [n.Identifier("a"), n.Identifier("b")]),
    ],
)
def test_parse_postfix_call(inner_source: str, args: list[n.Expr]) -> None:
    assert Parser(f"()({inner_source});").parse() == [
        n.ExprStmt(n.Postfix(n.UnitExpr.NULL, n.Call(args)))
    ]


def test_parse_postfix_call_fail() -> None:
    with pytest.raises(ParseError, match="expected `,` between arguments"):
        _ = Parser("()(a b);").parse()
