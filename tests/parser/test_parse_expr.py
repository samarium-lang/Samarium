import re
import pytest

from samarium import nodes as n
from samarium.parser import ParseError, Parser

NULL = n.UnitExpr.NULL
INULL = n.UnitExpr.IMPLICIT_NULL


@pytest.mark.parametrize(
    ("source", "expected_node"),
    [
        (
            "-+<-~~~**()",
            n.UnaryOp(
                [
                    n.UnOp.SUB,
                    n.UnOp.ADD,
                    n.UnOp.FROM,
                    n.UnOp.NOT,
                    n.UnOp.BNOT,
                    n.UnOp.YIELD,
                ],
                n.UnitExpr.NULL,
            ),
        ),
        (
            "-/+++/",
            n.UnaryOp([n.UnOp.SUB], n.BinaryOp(n.Int(1), n.BinOp.POW, n.Int(1))),
        ),
        (
            "(-/)+++/",
            n.BinaryOp(n.UnaryOp([n.UnOp.SUB], n.Int(1)), n.BinOp.POW, n.Int(1)),
        ),
        (
            "/+++-/",
            n.BinaryOp(n.Int(1), n.BinOp.POW, n.UnaryOp([n.UnOp.SUB], n.Int(1))),
        ),
        (
            "/+++/+++/",
            n.BinaryOp(
                n.Int(1), n.BinOp.POW, n.BinaryOp(n.Int(1), n.BinOp.POW, n.Int(1))
            ),
        ),
    ],
)
def test_parse_power_unary(source: str, expected_node: n.Expr) -> None:
    assert Parser(f"{source};").parse() == [n.ExprStmt(expected_node)]


@pytest.mark.parametrize(
    ("op_src", "op_obj"), [("&&", n.BinOp.AND), ("||", n.BinOp.OR)]
)
def test_parse_chained_logical(op_src: str, op_obj: n.BinOp) -> None:
    assert Parser(op_src.join("abcde") + ";").parse() == [
        n.ExprStmt(
            n.BinaryOp(
                n.Identifier("a"),
                op_obj,
                n.BinaryOp(
                    n.Identifier("b"),
                    op_obj,
                    n.BinaryOp(
                        n.Identifier("c"),
                        op_obj,
                        n.BinaryOp(n.Identifier("d"), op_obj, n.Identifier("e")),
                    ),
                ),
            )
        )
    ]


def test_parse_operator_precedence() -> None:
    # Aliases to make the expected output more digestible
    b, bo, u, uo, i = n.BinaryOp, n.BinOp, n.UnaryOp, n.UnOp, n.UnitExpr.IMPLICIT_NULL

    ast = Parser(
        "--- > ->? && >: + ^ ::: >< < >< ::: ~~ + ++ < &&"
        " <: - ::: ::: + || :: () ~~ ->? && :: +++ & -- & |;"
    ).parse()

    assert len(ast) == 1 and isinstance(ast[0], n.ExprStmt)
    assert ast[0].expr == b(
        b(
            b(b(b(i, bo.MOD, i), bo.GT, i), bo.AND, b(i, bo.IN, i)),
            bo.AND,
            b(
                b(
                    b(i, bo.GE, b(u([uo.ADD], i), bo.BXOR, i)),
                    bo.AND,
                    b(
                        b(b(u([uo.ADD], i), bo.BXOR, i), bo.NE, b(i, bo.ZIP, i)),
                        bo.AND,
                        b(
                            b(b(i, bo.ZIP, i), bo.LT, b(i, bo.ZIP, i)),
                            bo.AND,
                            b(
                                b(
                                    b(i, bo.ZIP, i),
                                    bo.NE,
                                    b(u([uo.NOT, uo.ADD], i), bo.MUL, i),
                                ),
                                bo.AND,
                                b(b(u([uo.NOT, uo.ADD], i), bo.MUL, i), bo.LT, i),
                            ),
                        ),
                    ),
                ),
                bo.AND,
                b(
                    b(i, bo.LE, u([uo.SUB], i)),
                    bo.AND,
                    b(b(u([uo.SUB], i), bo.NE, i), bo.AND, b(i, bo.NE, u([uo.ADD], i))),
                ),
            ),
        ),
        bo.OR,
        b(
            b(b(i, bo.EQ, NULL), bo.AND, b(b(NULL, bo.NIN, i), bo.AND, b(i, bo.IN, i))),
            bo.AND,
            b(
                i,
                bo.EQ,
                b(
                    b(b(b(i, bo.POW, i), bo.BAND, b(i, bo.DIV, i)), bo.BAND, i),
                    bo.BOR,
                    i,
                ),
            ),
        ),
    )


def test_pec() -> None:
    print(Parser(r"~((>w<))~;").parse())
    assert False