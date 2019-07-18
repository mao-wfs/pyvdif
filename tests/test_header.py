# coding: utf-8
import pytest

from pyvdif import make_parser


class TestMakeParser:
    words = (
        14363767,
        469762048,
        536871541,
        67239932,
        58720272,
        2896953069,
        859832320,
        4060288387,
    )

    @pytest.mark.parametrize(
        "word_index, bit_index, bit_length, expected",
        [(0, 0, 30, 14363767), (1, 24, 6, 28), (3, 31, 1, 0)],
    )
    def test_success(
        self, word_index: int, bit_index: int, bit_length: int, expected: int
    ):
        parser = make_parser(word_index, bit_index, bit_length)
        assert parser(self.words) == expected

    @pytest.mark.parametrize(
        "word_index, bit_index, bit_length", [(0, 0, 33), (1, 24, 16), (3, 31, 2)]
    )
    def test_failure(self, word_index: int, bit_index: int, bit_length: int):
        with pytest.raises(ValueError):
            _ = make_parser(word_index, bit_index, bit_length)
