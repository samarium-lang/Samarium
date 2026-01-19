from __future__ import annotations

import string
from typing import TYPE_CHECKING, NamedTuple

import bitstruct.c as bitstruct

from samarium.tokenizer import Tokenlike
from samarium.tokens import Token

if TYPE_CHECKING:
    from collections.abc import Iterable

IDENT_CHARSET = "\0" + string.ascii_letters + string.digits + "_"


class SourceData(NamedTuple):
    tokens: list[int]
    identifier_table: list[str]
    string_table: list[str]
    int_table: list[int]
    float_table: list[tuple[int, int]]


def group_tokens(
    tokens: Iterable[Tokenlike],
) -> SourceData:
    token_ids: list[int] = []
    ident_table: list[str] = []
    string_table: list[str] = ['""']
    int_table: list[int] = []
    float_table: list[tuple[int, int]] = []
    for tok in tokens:
        if isinstance(tok, Token):
            token_ids.append(tok.index)
        elif isinstance(tok, tuple):
            token_ids.append(Token.FLOAT.index)
            if tok not in float_table:
                float_table.append(tok)
            token_ids.extend(get_length(float_table.index(tok), 7))
        elif isinstance(tok, int):
            token_ids.append(Token.INT.index)
            if tok not in int_table:
                int_table.append(tok)
            token_ids.extend(get_length(int_table.index(tok), 7))
        elif tok.startswith('"'):
            token_ids.append(Token.STRING.index)
            if tok not in string_table:
                string_table.append(tok)
            token_ids.extend(get_length(string_table.index(tok), 7))
        else:
            token_ids.append(Token.IDENTIFIER.index)
            if tok not in ident_table:
                ident_table.append(tok)
            token_ids.extend(get_length(ident_table.index(tok), 7))
    return SourceData(token_ids, ident_table, string_table, int_table, float_table)


def get_length(length: int, bits: int) -> list[int]:
    chunk_size = (1 << bits) - 1
    chunks, remainder = divmod(length, chunk_size)
    return [*[chunk_size] * chunks, remainder]


def pack_idents(ident_table: list[str]) -> list[int]:
    packed: list[int] = []
    for ident in ident_table:
        packed.extend(get_length(len(ident), 6))
        packed.extend(map(IDENT_CHARSET.find, ident))
    packed.append(0)
    return packed


def pack_strings(string_table: list[str]) -> list[int]:
    packed: list[int] = []
    for string in string_table:
        content = string[1:-1].encode("utf-8")
        if not content:
            continue
        packed.extend(get_length(len(content), 8))
        packed.extend(content)
    packed.append(0)
    return packed


def to_nibbles(x: int) -> list[int]:
    nibbles: list[int] = []
    while x:
        nibbles.append(x & 0xF)
        x >>= 4
    return nibbles[::-1] or [0]


def pack_ints(int_table: list[int]) -> list[int]:
    packed: list[int] = []
    for int_ in int_table:
        nibs = to_nibbles(int_)
        packed.extend(get_length(len(nibs), 4))
        packed.extend(nibs)
    packed.append(0)
    return packed


def pack_floats(float_table: list[tuple[int, int]]) -> list[int]:
    packed: list[int] = []
    for dec, frac in float_table:
        dec_nibs = to_nibbles(dec)
        packed.extend(get_length(len(dec_nibs), 4))
        if frac:
            frac_nibs = to_nibbles(frac)
            packed.extend(get_length(len(frac_nibs), 4))
            packed.extend(dec_nibs)
            packed.extend(frac_nibs)
        else:
            packed.append(0)
            packed.extend(dec_nibs)
    packed.append(0)
    return packed


def compress(tokens: Iterable[Tokenlike]) -> bytes:
    token_ids, ident_table, string_table, int_table, float_table = group_tokens(tokens)
    token_ids.append(0)
    idents = pack_idents(ident_table)
    strings = pack_strings(string_table)
    ints = pack_ints(int_table)
    floats = pack_floats(float_table)
    fmt = (
        "u7" * len(token_ids)
        + "u6" * len(idents)
        + "u8" * len(strings)
        + "u4" * (len(ints) + len(floats))
    )
    return bitstruct.pack(fmt, *token_ids, *idents, *strings, *ints, *floats)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    from samarium.tokenizer import tokenize

    tokens = tokenize(Path(sys.argv[1]).read_text())
    _ = sys.stdout.buffer.write(compress(tokens))
