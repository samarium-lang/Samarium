import pytest

from samarium.parser import ParseError, parse
from syrupy.assertion import SnapshotAssertion


@pytest.mark.parametrize("inner_source", ["", ",", "()", "(), , ,()", "a,b", "a,b,"])
def test_parse_postfix_call(inner_source: str, snapshot: SnapshotAssertion) -> None:
    assert parse(f"()({inner_source});") == snapshot


def test_parse_postfix_repeated_call(snapshot: SnapshotAssertion) -> None:
    assert parse("()()()();") == snapshot


def test_parse_postfix_call_fail() -> None:
    with pytest.raises(ParseError, match="expected `,` between arguments"):
        _ = parse("()(a b);")


def test_parse_postfix_attr(snapshot: SnapshotAssertion) -> None:
    assert parse("3.14;") == snapshot


@pytest.mark.parametrize("op", ["???", "??", "?!", "!", "!?", "##", "$", "**", "%"])
def test_parse_postfix_op(op: str, snapshot: SnapshotAssertion) -> None:
    assert parse(f"(){op};") == snapshot


def test_parse_postfix_op_multiple(snapshot: SnapshotAssertion) -> None:
    assert parse(f"()?????!?!$?!**%##;") == snapshot


def test_parse_postfix_attr_fail() -> None:
    with pytest.raises(ParseError, match=r"expected attribute name after `\.`"):
        _ = parse("a.;")
