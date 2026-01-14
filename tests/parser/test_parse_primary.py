import re
import pytest

from samarium import nodes as n
from samarium.parser import ParseError, Parser

NULL = n.UnitExpr.NULL
INULL = n.UnitExpr.IMPLICIT_NULL


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
        (r"[... ->? [] ?]", n.ArrayComp(n.Array([]), [], INULL, INULL)),
        (r"{{}}", n.Table([])),
        (r"{{->,->}}", n.Table([(INULL, INULL), (INULL, INULL)])),
        (r"{{->,->,}}", n.Table([(INULL, INULL), (INULL, INULL)])),
        (r"{{->...->?()?}}", n.TableComp(NULL, [], (INULL, INULL), INULL)),
        (
            r"{{->...0,->?()?}}",
            n.TableComp(NULL, [n.Identifier("0")], (INULL, INULL), INULL),
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
        (r"", INULL),
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
    ("start", "stop", "step", "inner_source"),
    [
        (NULL, NULL, NULL, r""),
        (NULL, NULL, NULL, r".."),
        (NULL, NULL, INULL, r"...."),
        (n.Int(1), NULL, NULL, r"/.."),
        (n.Int(1), NULL, INULL, r"/...."),
        (NULL, n.Int(1), NULL, r"../"),
        (NULL, n.Int(1), NULL, r"../.."),
        (NULL, NULL, n.Int(1), r"..../"),
        (NULL, n.Int(1), n.Int(1), r"../../"),
        (n.Int(1), NULL, n.Int(1), r"/..../"),
        (n.Int(1), n.Int(1), INULL, r"/../.."),
        (n.Int(1), n.Int(1), n.Int(1), r"/../../"),
    ],
)
def test_parse_primary_slice(
    inner_source: str,
    start: n.Int | n.UnitExpr,
    stop: n.Int | n.UnitExpr,
    step: n.Int | n.UnitExpr,
) -> None:
    assert Parser(f"<<{inner_source}>>;").parse() == [
        n.ExprStmt(n.Slice(start, stop, step))
    ]


@pytest.mark.parametrize("source", ["#", "'#"])
def test_parse_primary_identifer_fail(source: str) -> None:
    with pytest.raises(ParseError, match=re.escape(f"expected a name after {source}")):
        _ = Parser(source).parse()


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        (r"<<..b..c;", "`<<` was never closed"),
        (r"<<..b?", "`<<` was never closed"),
        (r"<<..@", "`<<` was never closed"),
        (r"<<a b>>", "missing `..` between slice items"),
        (r"<<a;", "`<<` was never closed"),
        (r"<<a..b;", "`<<` was never closed"),
        (r"<<a..b c;", "missing `..` between slice items"),
        (r"<<...x>>", "expected `<<..` or `<<....`, not `<<...`"),
        (r"<<a....>", "`<<` was never closed"),
        (r"<<a.. ..>", "`<<` was never closed"),
        (r"<<a..b..;", "`<<` was never closed"),
        (r"<<a...>", "expected `<<a..` or `<<a....`, not `<<a...`"),
    ],
)
def test_parse_primary_slice_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = Parser(source).parse()


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("{{x y ... ->?}}", "expected a `k -> v` pair"),
        ("{{k -> v .. ->?}}", "expected `...` after pair in table comprehension"),
        ("{{k -> v ... a b ->?}}", "missing `,` between table comprehension targets"),
        ("{{-> ... / ->?}}", "expected identifier as a table comprehension target"),
        ("{{->...->?", "`{{` was never closed"),
        ("{{k v}}", "expected a `k -> v` pair"),
        ("{{k -> v,", "expected a `k -> v` pair"),
        ("{{k -> v", "expected `...` after pair in table comprehension"),
        ("{{k -> v, l -> w  m -> x}}", "missing `,` between table pairs"),
        ("[a, b c]", "missing `,` between array items"),
        ("[x .. ->?]", "expected `...` after item in array comprehension"),
        ("[x ... a b ->?]", "missing `,` between array comprehension targets"),
        ("[... / ->?]", "expected identifier as an array comprehension target"),
        ("[...->?", "`[` was never closed"),
    ],
)
def test_parse_primary_collections_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = Parser(source).parse()


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("(0", "`(` was never closed"),
    ],
)
def test_parse_primary_basic_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = Parser(source).parse()
