import re
import pytest

from samarium.parser import ParseError, parse
from syrupy.assertion import SnapshotAssertion


@pytest.mark.parametrize(
    "source",
    [
        "@! Foo;",
        "@! Foo();",
        "@! Foo() {}",
        "@! Foo {}",
        "@! Person(name, age);",
        "@! Person(name, age,);",
        "@!0{ a*{} }",
    ],
)
def test_parse_data_class_stmt(source: str, snapshot: SnapshotAssertion) -> None:
    assert parse(source) == snapshot


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
        _ = parse(source)


@pytest.mark.parametrize("source", ["@ => { hey * { } }", "@0{}", "@ a(b, c) {}"])
def test_parse_class_def_stmt(source: str, snapshot: SnapshotAssertion) -> None:
    assert parse(source) == snapshot


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("@", "expected identifier or `=>` as class name"),
        ("@ Foo", "expected block after class definition"),
        ("@ Foo(a, b)", "expected block after class definition"),
        ("@ Foo(a b)", "expected `,` between class parents"),
        ("@ Foo(a, b, ,)", "expected class parent"),
    ],
)
def test_parse_class_def_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = parse(source)


@pytest.mark.parametrize(
    "source",
    [
        "hey * {}",
        "?what? * {}",
        "hey who? ~'* {}",
        "hey who... ~'* {}",
        "dont @ me ok... * {}",
        "=> * {}",
        "->? * {}",
        "++ * {}",
        "+ * {}",
        "+a * {}",
        "-_ * {}",
        "<<>> * {}",
        "<<>>: * {}",
        'hey who * { "hey"!; }',
    ],
)
def test_parse_func_def_stmt(source: str, snapshot: SnapshotAssertion) -> None:
    assert parse(source) == snapshot


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("foo bar baz", "expected parameter"),
        ("foo bar baz /", "expected parameter"),
        ("foo bar baz ~*", "expected `*` or `~'*`"),
        ("hey * * {}", "expected block after function definition"),
        ("hey *", "expected block after function definition"),
    ],
)
def test_parse_func_def_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = parse(source)


def test_parse_try_stmt(snapshot: SnapshotAssertion) -> None:
    assert parse(r"?? { /--\; } !! { \--/; }") == snapshot


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("??", "expected block after `??`"),
        ("?? {}", "expected `!!` after `??` block"),
        ("?? {} !!", "expected block after `!!`"),
    ],
)
def test_parse_try_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = parse(source)


def test_parse_while_stmt(snapshot: SnapshotAssertion) -> None:
    assert parse(r".. / { /!; }") == snapshot


def test_parse_while_stmt_fail() -> None:
    with pytest.raises(ParseError, match=r"expected block after `\.\.` condition"):
        _ = parse(".. /")


@pytest.mark.parametrize(
    "source", ["...->?{}", "...a->?{}", "...a,->?{}", "...a,b->?c{d;}"]
)
def test_parse_foreach_stmt(source: str, snapshot: SnapshotAssertion) -> None:
    assert parse(source) == snapshot


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("... a b ->?{}", "expected `,` between loop targets"),
        ("... , ->?{}", "expected loop target"),
        ("...->?", "expected block after loop definition"),
    ],
)
def test_parse_foreach_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = parse(source)


@pytest.mark.parametrize(
    "source",
    ["? {}", "? {} ,, {}", "? {} ,, ? {}", "? {} ,, ? {} ,, {}", "? a {;} ,, {;}"],
)
def test_parse_if_stmt(source: str, snapshot: SnapshotAssertion) -> None:
    assert parse(source) == snapshot


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("?", "expected block after `?` condition"),
        ("? {} ,,", "expected block or `?` after `,,`"),
    ],
)
def test_parse_if_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = parse(source)
