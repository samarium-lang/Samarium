from __future__ import annotations

import re
import pytest

from samarium.parser import ParseError, parse
from syrupy.assertion import SnapshotAssertion


@pytest.mark.parametrize("source", [";;", "!!!", "!!!();();", "!!!;();"])
def test_parse_expr_or_throw_stmt(source: str, snapshot: SnapshotAssertion) -> None:
    assert parse(source) == snapshot


@pytest.mark.parametrize(
    ("source", "error_message"),
    [("hey", "expected `;` after the expression"), ("<>", "unexpected token `<>`")],
)
def test_parse_expr_or_throw_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = parse(source)


@pytest.mark.parametrize(
    "source", ["<=0;", "<=0.*;", "<=0.1;", "<=0.[];", "<=0.[1, 2];", "<=0.[1 -> 2];"]
)
def test_parse_import_stmt(source: str, snapshot: SnapshotAssertion) -> None:
    assert parse(source) == snapshot


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
        _ = parse(source)


def test_parse_default_stmt(snapshot: SnapshotAssertion) -> None:
    assert parse("0<>;") == snapshot


def test_parse_default_stmt_fail() -> None:
    with pytest.raises(ParseError, match="expected `;` after default value"):
        _ = parse("0<>")


@pytest.mark.parametrize("source", ["0 # {}", "0 # { a; }", "0 # { a: /; }"])
def test_parse_enum_stmt(source: str, snapshot: SnapshotAssertion) -> None:
    assert parse(source) == snapshot


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
        _ = parse(source)


def test_parse_file_io_stmt_create(snapshot: SnapshotAssertion) -> None:
    assert parse("?~>;") == snapshot


@pytest.mark.parametrize(
    "op",
    [
        "&~~>",
        "<~~",
        "~~>",
        "<~>",
        "&%~>",
        "<~%",
        "%~>",
        "<%>",
        "&~>",
        "<~",
        "~>",
        "&%>",
        "<%",
        "%>",
    ],
)
def test_parse_file_io_stmt_access(op: str, snapshot: SnapshotAssertion) -> None:
    assert parse(f"a {op} b;") == snapshot


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
        _ = parse(source)


@pytest.mark.parametrize("source", ["x:;", "a,b+:;", "a<<>>,b,c<</..>>,d^:;"])
def test_parse_assignment_stmt(source: str, snapshot: SnapshotAssertion) -> None:
    assert parse(source) == snapshot


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("x ~ : 5;", "invalid assignment operator `~:`"),
        ("0:", "expected `;` after assignment statement"),
    ],
)
def test_parse_assignment_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = parse(source)


@pytest.mark.parametrize("ending", [";", ""])
def test_parse_yield_stmt_ending(ending: str, snapshot: SnapshotAssertion) -> None:
    assert parse(f".. {{ ** x{ending} }}") == snapshot


def test_parse_yield_stmt_fail() -> None:
    with pytest.raises(
        ParseError, match="expected `;` or block end after yield statement"
    ):
        _ = parse("** x")


@pytest.mark.parametrize("ending", [";", ""])
def test_parse_return_stmt_ending(ending: str, snapshot: SnapshotAssertion) -> None:
    assert parse(f".. {{ * x{ending} }}") == snapshot


def test_parse_return_stmt_fail() -> None:
    with pytest.raises(
        ParseError, match="expected `;` or block end after return statement"
    ):
        _ = parse("* x")


@pytest.mark.parametrize("source", ["!!;", "!!,;"])
def test_parse_assert_stmt(source: str, snapshot: SnapshotAssertion) -> None:
    assert parse(source) == snapshot


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("!!", "expected `,` or `;` after assert expression"),
        ("!!,", "expected `;` after assert message"),
    ],
)
def test_parse_assert_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = parse(source)


def test_parse_sleep_stmt(snapshot: SnapshotAssertion) -> None:
    assert parse(",.,;") == snapshot


def test_parse_sleep_stmt_fail() -> None:
    with pytest.raises(ParseError, match="expected `;` after sleep statement"):
        _ = parse(",.,")


def test_parse_exit_stmt(snapshot: SnapshotAssertion) -> None:
    assert parse("=>!;") == snapshot


def test_parse_exit_stmt_fail() -> None:
    with pytest.raises(ParseError, match="expected `;` after exit statement"):
        _ = parse("=>!")


@pytest.mark.parametrize("ending", [";", ""])
def test_parse_break_stmt_ending(ending: str, snapshot: SnapshotAssertion) -> None:
    assert parse(f".. {{ <-{ending} }}") == snapshot


@pytest.mark.parametrize("ending", [";", ""])
def test_parse_continue_stmt_ending(ending: str, snapshot: SnapshotAssertion) -> None:
    assert parse(f".. {{ ->{ending} }}") == snapshot
