import re
import pytest

from samarium import nodes as n
from samarium.parser import ParseError, Parser

NULL = n.UnitExpr.NULL


@pytest.mark.parametrize(
    ("source", "expected_node"),
    [
        (r"[]", n.Array([])),
        (r"[/,]", n.Array([n.Int(1)])),
        (r"[/\, //]", n.Array([n.Int(2), n.Int(3)])),
        (r"[[],(),[]]", n.Array([n.Array([]), NULL, n.Array([])])),
        (
            r"[0 ... 0 ->? 1]",
            n.ArrayComp(
                n.Identifier("1"), [n.Identifier("0")], n.Identifier("0"), None
            ),
        ),
        (
            r"[... ->? [] ?]",
            n.ArrayComp(n.Array([]), [], NULL, NULL),
        ),
        (r"{{}}", n.Table([])),
        (
            r"{{->,->}}",
            n.Table([(NULL, NULL), (NULL, NULL)]),
        ),
        (
            r"{{->...->?()?}}",
            n.TableComp(NULL, [], (NULL, NULL), NULL),
        ),
        (
            r"{{{{}}->{{}}...->?[]?[]}}",
            n.TableComp(n.Array([]), [], (n.Table([]), n.Table([])), n.Array([])),
        ),
    ],
)
def test_parse_primary_collections(source: str, expected_node: n.Expr) -> None:
    assert Parser(source + ";").parse() == [n.ExprStmt(expected_node)]


@pytest.mark.parametrize(
    ("source", "expected_node"),
    [
        (r"//\\", n.Int(12)),
        (r"/\`\/", n.Float(2, 1)),
        (r'"hey"', n.String('"hey"')),
        (r"@@", n.UnitExpr.DATETIME),
        (r"@@@", n.UnitExpr.TIMESTAMP),
        (r"()", NULL),
        (r"", NULL),
        (r"(\)", n.Int(0)),
        (r"<<\>>", n.Index(n.Int(0))),
    ],
)
def test_parse_primary_basic(source: str, expected_node: n.Expr) -> None:
    assert Parser(source + ";").parse() == [n.ExprStmt(expected_node)]


@pytest.mark.parametrize(
    ("source", "expected_data"),
    [
        (r"0", ("0", False, False)),
        (r"'0", ("0", True, False)),
        (r"#0", ("0", False, True)),
        (r"'#0", ("0", True, True)),
        (r"'", (None, True, False)),
    ],
)
def test_parse_primary_identifier(
    source: str, expected_data: tuple[str | None, bool, bool]
) -> None:
    assert Parser(source + ";").parse() == [n.ExprStmt(n.Identifier(*expected_data))]


@pytest.mark.parametrize(
    ("fields", "inner_source"),
    [
        ((0, 0, 0), r""),
        ((0, 0, 0), r".."),
        ((0, 0, 0), r"...."),
        ((1, 0, 0), r"/.."),
        ((1, 0, 0), r"/...."),
        ((0, 1, 0), r"../"),
        ((0, 1, 0), r"../.."),
        ((0, 0, 1), r"..../"),
        ((0, 1, 1), r"../../"),
        ((1, 0, 1), r"/..../"),
        ((1, 1, 0), r"/../.."),
        ((1, 1, 1), r"/../../"),
    ],
)
def test_parse_primary_slice(inner_source: str, fields: tuple[int, int, int]) -> None:
    slice = n.Slice(*(n.Int(1) if num else NULL for num in fields))
    assert Parser(f"<<{inner_source}>>;").parse() == [n.ExprStmt(slice)]


def test_parse_primary_identifer_fail() -> None:
    with pytest.raises(ParseError, match="expected a name after '#"):
        _ = Parser("'#").parse()


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        
    ],
)
def test_parse_primary_slice_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = Parser(source).parse()