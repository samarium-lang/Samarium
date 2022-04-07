from samarium import tokenizer
from samarium.tokens import Token


def _meta_test_tokens(string, expected_tokens):
    tokens = tokenizer.tokenize(string)
    assert len(tokens) == len(expected_tokens)
    for token, expected_token in zip(tokens, expected_tokens):
        assert token == expected_token


def test_arithmetics_tokens():
    _meta_test_tokens(
        "+-++--+++---",
        (Token.ADD, Token.SUB, Token.MUL, Token.DIV, Token.POW, Token.MOD)
    )


def test_comparison_tokens():
    _meta_test_tokens(
        ">: > <: < :: :::", 
        (Token.GE, Token.GT, Token.LE, Token.LT, Token.EQ, Token.NE)
    )
