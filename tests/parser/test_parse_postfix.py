import re
import pytest

from samarium import nodes as n
from samarium.parser import ParseError, Parser


@pytest.mark.parametrize(
    ("inner_source", "args"),
    [
        ("", []),
        (",", [n.INULL]),
        ("()", [n.NULL]),
        ("(), , ,()", [n.NULL, n.INULL, n.INULL, n.NULL]),
        ("a,b", [n.Identifier("a"), n.Identifier("b")]),
        ("a,b,", [n.Identifier("a"), n.Identifier("b")]),
    ],
)
def test_parse_postfix_call(inner_source: str, args: list[n.Expr]) -> None:
    assert Parser(f"()({inner_source});").parse() == [
        n.ExprStmt(n.Postfix(n.NULL, n.Call(args)))
    ]


def test_parse_postfix_repeated_call() -> None:
    assert Parser("()()()();").parse() == [
        n.ExprStmt(
            n.Postfix(
                n.Postfix(n.Postfix(n.NULL, n.Call([])), n.Call([])),
                n.Call([]),
            )
        )
    ]


def test_parse_postfix_call_fail() -> None:
    with pytest.raises(ParseError, match="expected `,` between arguments"):
        _ = Parser("()(a b);").parse()


def test_parse_postfix_attr() -> None:
    assert Parser("3.14;").parse() == [
        n.ExprStmt(n.Postfix(n.Identifier("3"), n.Attribute(n.Identifier("14"))))
    ]


@pytest.mark.parametrize(
    ("op", "postfix_kind"),
    [
        ("???", n.UnitPostfix.READLINE),
        ("??", n.UnitPostfix.RANDOM),
        ("?!", n.UnitPostfix.TYPE),
        ("!", n.UnitPostfix.PRINT),
        ("!?", n.UnitPostfix.PARENT),
        ("##", n.UnitPostfix.HASH),
        ("$", n.UnitPostfix.SPECIAL),
        ("**", n.UnitPostfix.ID),
        ("%", n.UnitPostfix.CAST),
    ],
)
def test_parse_postfix_op(op: str, postfix_kind: n.UnitPostfix) -> None:
    assert Parser(f"(){op};").parse() == [n.ExprStmt(n.Postfix(n.NULL, postfix_kind))]


def test_parse_postfix_op_multiple() -> None:
    assert Parser(f"()?????!?!$?!**%##;").parse() == [
        n.ExprStmt(
            n.Postfix(
                n.Postfix(
                    n.Postfix(
                        n.Postfix(
                            n.Postfix(
                                n.Postfix(
                                    n.Postfix(
                                        n.Postfix(
                                            n.Postfix(n.NULL, n.UnitPostfix.READLINE),
                                            n.UnitPostfix.RANDOM,
                                        ),
                                        n.UnitPostfix.PARENT,
                                    ),
                                    n.UnitPostfix.PRINT,
                                ),
                                n.UnitPostfix.SPECIAL,
                            ),
                            n.UnitPostfix.TYPE,
                        ),
                        n.UnitPostfix.ID,
                    ),
                    n.UnitPostfix.CAST,
                ),
                n.UnitPostfix.HASH,
            )
        )
    ]


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("a.;", "expected attribute name after `.`"),
        ("a.';", "cannot use `'` as an attribute name"),
    ],
)
def test_parse_postfix_attr_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = Parser(source).parse()
