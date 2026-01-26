import pytest

from samarium.parser import ParseError, Parser
from syrupy.assertion import SnapshotAssertion


@pytest.mark.parametrize("inner_source", ["", ",", "()", "(), , ,()", "a,b", "a,b,"])
def test_parse_postfix_call(inner_source: str, snapshot: SnapshotAssertion) -> None:
    assert Parser(f"()({inner_source});").parse() == snapshot


def test_parse_postfix_repeated_call(snapshot: SnapshotAssertion) -> None:
    assert Parser("()()()();").parse() == snapshot


def test_parse_postfix_call_fail() -> None:
    with pytest.raises(ParseError, match="expected `,` between arguments"):
        _ = Parser("()(a b);").parse()


def test_parse_postfix_attr(snapshot: SnapshotAssertion) -> None:
    assert Parser("3.14;").parse() == snapshot


@pytest.mark.parametrize("op", ["???", "??", "?!", "!", "!?", "##", "$", "**", "%"])
def test_parse_postfix_op(op: str, snapshot: SnapshotAssertion) -> None:
    assert Parser(f"(){op};").parse() == snapshot


def test_parse_postfix_op_multiple(snapshot: SnapshotAssertion) -> None:
    assert Parser(f"()?????!?!$?!**%##;").parse() == snapshot


def test_parse_postfix_attr_fail() -> None:
    with pytest.raises(ParseError, match=r"expected attribute name after `\.`"):
        _ = Parser("a.;").parse()
