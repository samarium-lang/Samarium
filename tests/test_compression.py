import string
from hypothesis import given, settings
from hypothesis import strategies as st

from samarium.source_compressor import compress, group_tokens
from samarium.source_decompressor import decompress
from samarium.tokenizer import Tokenlike
from samarium.tokens import Token


@settings(max_examples=1000)
@given(
    st.lists(
        st.integers(min_value=1, max_value=80).map(Token.from_index)
        | st.text(alphabet=string.ascii_letters + string.digits + "_", min_size=1)
        | st.text().map(lambda x: x.join('""'))
        | st.tuples(st.integers(min_value=0), st.integers(min_value=0))
        | st.integers(min_value=0)
    )
)
def test_compression(inp: list[Tokenlike]) -> None:
    assert decompress(compress(inp)) == group_tokens(inp)
