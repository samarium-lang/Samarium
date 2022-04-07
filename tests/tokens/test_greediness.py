from samarium import tokenizer
from samarium.tokens import Token


def _meta_test_same(string, multiplier, expected_token):
    tokens = tokenizer.tokenize(string * multiplier)

    assert len(tokens) == multiplier
    assert set(tokens) == {expected_token}
    assert tokens[0] == expected_token


def test_tokenizer_greediness():
    _meta_test_same('+++', 7, Token.POW)
    _meta_test_same(':::', 7, Token.NE)
    _meta_test_same('---', 7, Token.MOD)
