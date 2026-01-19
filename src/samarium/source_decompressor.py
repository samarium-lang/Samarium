from __future__ import annotations

from itertools import chain
from typing import final

from samarium.source_compressor import IDENT_CHARSET, SourceData
from samarium.tokenizer import Tokenlike
from samarium.tokens import Token


@final
class BitBuffer:
    def __init__(self, buffer: bytes) -> None:
        self._bits = chain.from_iterable(f"{byte:08b}" for byte in buffer)

    def push_back(self, value: int, size: int) -> None:
        data = f"{value:0{size}b}"
        self._bits = chain(data, self._bits)

    def next(self, bits: int) -> int:
        bitstring = "".join(next(self._bits) for _ in range(bits))
        return int(bitstring, 2)


def gather_length(bit_buffer: BitBuffer, size: int) -> int:
    length = 0
    while True:
        batch = bit_buffer.next(size)
        length += batch
        if batch != (1 << size) - 1:
            return length


def decompress_tokens(bitbuf: BitBuffer) -> list[int]:
    tokens: list[int] = []
    null_allowed = False
    while (septet := bitbuf.next(7)) or null_allowed:
        null_allowed = False
        tokens.append(septet)
        if not septet:
            continue
        if septet > 80:
            # We're dealing with a literal now, so expect an index
            null_allowed = True
    return tokens


def decompress_ident_table(bitbuf: BitBuffer) -> list[str]:
    ident_table: list[str] = []
    while True:
        if not (sextet := bitbuf.next(6)):
            return ident_table
        bitbuf.push_back(sextet, 6)
        size = gather_length(bitbuf, 6)
        ident = (bitbuf.next(6) for _ in range(size))
        ident_table.append("".join(IDENT_CHARSET[c] for c in ident))


def decompress_string_table(bitbuf: BitBuffer) -> list[str]:
    string_table: list[str] = ['""']
    while True:
        if not (byte := bitbuf.next(8)):
            return string_table
        bitbuf.push_back(byte, 8)
        size = gather_length(bitbuf, 8)
        bytes_ = (bitbuf.next(8) for _ in range(size))
        string_table.append(bytes(bytes_).decode("utf-8").join('""'))


def decompress_int_table(bitbuf: BitBuffer) -> list[int]:
    int_table: list[int] = []
    while True:
        if not (nibble := bitbuf.next(4)):
            return int_table
        bitbuf.push_back(nibble, 4)
        size = gather_length(bitbuf, 4)
        int_table.append(bitbuf.next(4 * size))


def decompress_float_table(bitbuf: BitBuffer) -> list[tuple[int, int]]:
    float_table: list[tuple[int, int]] = []
    while True:
        if not (nibble := bitbuf.next(4)):
            return float_table
        bitbuf.push_back(nibble, 4)
        dec_size = gather_length(bitbuf, 4)
        frac_size = gather_length(bitbuf, 4)
        dec = bitbuf.next(4 * dec_size)
        frac = bitbuf.next(4 * frac_size) if frac_size else 0
        float_table.append((dec, frac))


def build_token_list(
    tokens: list[int],
    ident_table: list[str],
    string_table: list[str],
    int_table: list[int],
    float_table: list[tuple[int, int]],
) -> list[Tokenlike]:
    built_tokens: list[Tokenlike] = []
    for i, tok in enumerate(tokens):
        if tok > 80:
            continue
        if i and (prev := tokens[i - 1]) > 80:
            table = {81: ident_table, 82: string_table, 83: int_table, 84: float_table}
            built_tokens.append(table[prev][tok])
        else:
            built_tokens.append(Token.from_index(tok))
    return built_tokens


def decompress(minified: bytes) -> SourceData:
    bitbuf = BitBuffer(minified)
    return SourceData(
        decompress_tokens(bitbuf),
        decompress_ident_table(bitbuf),
        decompress_string_table(bitbuf),
        decompress_int_table(bitbuf),
        decompress_float_table(bitbuf),
    )
