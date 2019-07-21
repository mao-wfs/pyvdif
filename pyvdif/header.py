# coding: utf-8
from typing import Callable, Sequence


def make_parser(
    word_index: int, bit_index: int, bit_length: int
) -> Callable[[Sequence[int]], int]:
    """Construct a function that converts specific bits from a header.

    The function this returns acts on tuple/array of 32-bits words,
    extracting given bits from a specific word and convert them to a integer.
    The parameters are those that define header keywords, and the parser do
    ``(words[word_index] >> bit_index) & ((1 << bit_length) - 1)``.

    Note:
        As a special case, bit_length=64 allows one to extract two words
        as a single (long) integer.

    Args:
        word_index: Index into the tuple of words passed to the function.
        bit_index: Index to the starting bit of the part of be extracted.
        bit_length: Number of bits to be extracted.

    Return:
        A converter of specific bits from a header.

    Raises:
        ValueError:
          - If bit_index is not equal to 0 when bit_length is 64.
          - If the sum of bit_index and bit_length
            is less or equal to 0 or greater than 32.
    """
    if bit_length == 64:
        if bit_index != 0:
            raise ValueError(
                "bit_index is expected to be 0 when bit_length is 64, "
                f"got {bit_index}"
            )

        def parser(words: Sequence[int]) -> int:
            return words[word_index] + (words[word_index + 1] << 32)

    else:
        if not 0 < bit_index + bit_length <= 32:
            raise ValueError(
                "the sum of `bit_index` and `bit_length` expected "
                "to be greater than 0 and less or equal to 32, "
                f"got {bit_index + bit_length}"
            )

        def parser(words: Sequence[int]) -> int:
            bit_mask = (1 << bit_length) - 1
            return (words[word_index] >> bit_index) & bit_mask

    return parser
