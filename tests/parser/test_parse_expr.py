import pytest
from syrupy.assertion import SnapshotAssertion

from samarium.parser import Parser


@pytest.mark.parametrize(
    "source", ["-+<-~~~**()", "-/+++/", "(-/)+++/", "/+++-/", "/+++/+++/"]
)
def test_parse_power_unary(source: str, snapshot: SnapshotAssertion) -> None:
    assert Parser(f"{source};").parse() == snapshot


@pytest.mark.parametrize("op", ["&&", "||"])
def test_parse_chained_logical(op: str, snapshot: SnapshotAssertion) -> None:
    assert Parser(op.join("abcde") + ";").parse() == snapshot


def test_parse_operator_precedence(snapshot: SnapshotAssertion) -> None:
    assert (
        Parser(
            "--- > ->? && >: + ^ ::: >< < >< ::: ~~ + ++ < &&"
            " <: - ::: ::: + || :: () ~~ ->? && :: +++ & -- & |;"
        ).parse()
        == snapshot
    )
