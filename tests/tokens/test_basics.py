from samarium import tokenizer
from samarium.tokens import Token


def test_arithmetics_tokens():
    tokens = tokenizer.tokenize("+-++--+++---")
    assert len(tokens) == 6

    _expected_tokens = [Token.ADD, Token.SUB, Token.MUL, Token.DIV, Token.POW, Token.MOD]
    for token, expected_token in zip(tokens, _expected_tokens):
        assert token._value_ == expected_token.value


def test_comparison_tokens():
    tokens = tokenizer.tokenize(">: > <: < :: :::")
    assert len(tokens) == 6

    _expected_tokens = [Token.GE, Token.GT, Token.LE, Token.LT, Token.EQ, Token.NE]
    for token, expected_token in zip(tokens, _expected_tokens):
        assert token._value_ == expected_token.value
