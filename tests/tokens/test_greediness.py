from samarium import tokenizer
from samarium.tokens import Token


def _meta_test_same(string, multiplier, expected_token):
    tokens = tokenizer.tokenize(string * multiplier)
    if len(tokens) != multiplier:
        return False

    return all(
        token._value_ == expected_token.value
        for token in tokens
    )


def test_tokenizer_greediness():
    assert _meta_test_same('+++', 7, Token.POW)
    assert _meta_test_same(':::', 7, Token.NE)
    assert _meta_test_same('---', 7, Token.MOD)
