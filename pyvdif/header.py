# coding: utf-8
from typing import Callable, Sequence

Words = Sequence[int]
Parser = Callable[[Words], int]


def make_parser(word_index: int, bit_index: int, bit_length: int) -> Parser:
    """Construct a function that converts specific bits from a header.

    The function acts on a tuple/array of 32-bits words, extracting given bits
    from a specific word and convert then to a integer.
    The parameters are those that define header keywords, and the parser do
    ``(words[word_index] >> bit_index) & ((1 << bit_length) - 1)``.

    Args:
        word_index (int): Index into the tuple of words passed to the function.
        bit_index (int): Index to the starting bit of the part to be extracted.
        bit_length (int): Number of bits to be extracted.

    Return:
        parser (function): A converter of specific bits from a header.

    Raises:
        ValueError: If the sum of `bit_index` and `bit_length`
            is less or equal to 0 or greater than 32.
    """
    if not 0 < bit_index + bit_length <= 32:
        raise ValueError(
            "the sum of `bit_index` and `bit_length` expected "
            "to be greater than 0 and less or equal to 32, "
            f"got {bit_index + bit_length}"
        )

    def parser(words: Words) -> int:
        bit_mask = (1 << bit_length) - 1
        return (words[word_index] >> bit_index) & bit_mask

    return parser
