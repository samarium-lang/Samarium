import re
import pytest

from samarium.parser import ParseError, Parser
from syrupy.assertion import SnapshotAssertion


@pytest.mark.parametrize(
    "source",
    [
        r"[]",
        r"[/,]",
        r"[/\, //]",
        r"[[],(),[]]",
        r"[[], ,[]]",
        r"[0 ... 0 ->? 1]",
        r"[... ->? [] ?]",
        r"[...->??]",
        r"{{}}",
        r"{{->,->}}",
        r"{{->,->,}}",
        r"{{->...->?()?}}",
        r"{{->...0,->?()?}}",
        r"{{{{}}->{{}}...->?[]?[]}}",
    ],
)
def test_parse_primary_collections(source: str, snapshot: SnapshotAssertion) -> None:
    assert Parser(source + ";").parse() == snapshot


@pytest.mark.parametrize(
    "source", [r"//\\", r"/\`\/", r'"hey"', r"@@", r"@@@", r"()", r"", r"(\)", r"<<\>>"]
)
def test_parse_primary_basic(source: str, snapshot: SnapshotAssertion) -> None:
    assert Parser(source + ";").parse() == snapshot


@pytest.mark.parametrize("source", [r"0", r"'0", r"#0", r"'#0", r"'"])
def test_parse_primary_identifier(source: str, snapshot: SnapshotAssertion) -> None:
    assert Parser(source + ";").parse() == snapshot


@pytest.mark.parametrize(
    "inner_source",
    [
        r"",
        r"..",
        r"....",
        r".. ..",
        r"/..",
        r"/....",
        r"../",
        r"../..",
        r"..../",
        r".. ../",
        r"../../",
        r"/..../",
        r"/.. ../",
        r"/../..",
        r"/../../",
    ],
)
def test_parse_primary_slice(inner_source: str, snapshot: SnapshotAssertion) -> None:
    assert Parser(f"<<{inner_source}>>;").parse() == snapshot


@pytest.mark.parametrize("source", ["#", "'#"])
def test_parse_primary_identifer_fail(source: str) -> None:
    with pytest.raises(ParseError, match=re.escape(f"expected a name after {source}")):
        _ = Parser(source).parse()


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        (r"<<..b..c;", "`<<` was never closed"),
        (r"<<..b?", "expected `,,` after `?` expression"),
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
        ("{{k -> v ... a b ->?}}", "expected `,` between table comprehension targets"),
        ("{{-> ... / ->?}}", "expected table comprehension target"),
        ("{{->...->?", "`{{` was never closed"),
        ("{{k v}}", "expected a `k -> v` pair"),
        ("{{k -> v,", "expected a `k -> v` pair"),
        ("{{k -> v", "expected `...` after pair in table comprehension"),
        ("{{k -> v, l -> w  m -> x}}", "missing `,` between table pairs"),
        ("[a, b c]", "missing `,` between array items"),
        ("[x .. ->?]", "expected `...` after item in array comprehension"),
        ("[x ... a b ->?]", "expected `,` between array comprehension targets"),
        ("[... / ->?]", "expected array comprehension target"),
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
