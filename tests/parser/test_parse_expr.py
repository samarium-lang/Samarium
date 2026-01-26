import pytest
from syrupy.assertion import SnapshotAssertion

from samarium.parser import parse


@pytest.mark.parametrize(
    "source", ["-+<-~~~**()", "-/+++/", "(-/)+++/", "/+++-/", "/+++/+++/"]
)
def test_parse_power_unary(source: str, snapshot: SnapshotAssertion) -> None:
    assert parse(f"{source};") == snapshot


@pytest.mark.parametrize("op", ["&&", "||"])
def test_parse_chained_logical(op: str, snapshot: SnapshotAssertion) -> None:
    assert parse(op.join("abcde") + ";") == snapshot


def test_parse_operator_precedence(snapshot: SnapshotAssertion) -> None:
    assert (
        parse(
            "--- > ->? && >: + ^ ::: >< < >< ::: ~~ + ++ < &&"
            " <: - ::: ::: + || :: () ~~ ->? && :: +++ & -- & |;"
        )
        == snapshot
    )
