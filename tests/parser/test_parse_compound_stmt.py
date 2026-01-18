import re
import pytest

from samarium import nodes as n
from samarium.parser import ParseError, Parser

NULL = n.UnitExpr.NULL
INULL = n.UnitExpr.IMPLICIT_NULL


@pytest.mark.parametrize(
    ("source", "name", "members", "block"),
    [
        ("@! Foo;", "Foo", [], None),
        ("@! Foo();", "Foo", [], None),
        ("@! Foo() {}", "Foo", [], n.Block([])),
        ("@! Foo {}", "Foo", [], n.Block([])),
        ("@! Person(name, age);", "Person", ["name", "age"], None),
        ("@! Person(name, age,);", "Person", ["name", "age"], None),
        (
            "@!0{ a*{} }",
            "0",
            [],
            n.Block([n.FuncDef(n.Identifier("a"), [], False, n.Block([]), [])]),
        ),
    ],
)
def test_parse_data_class_stmt(
    source: str, name: str, members: list[str], block: n.Block | None
) -> None:
    assert Parser(source).parse() == [
        n.DataClassDef(n.Identifier(name), list(map(n.Identifier, members)), block)
    ]


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("@!", "expected data class name"),
        ("@! Foo", "expected `;` or block after data class definition"),
        ("@! Foo(a, b)", "expected `;` or block after data class definition"),
        ("@! Foo(a b)", "expected `,` between data class members"),
        ("@! Foo(a, b, ,)", "expected data class member"),
    ],
)
def test_parse_data_class_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = Parser(source).parse()
