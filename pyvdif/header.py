from typing import Callable, Dict, Sequence, Union


def make_header_parser(
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


class VDIFHeader:
    """VDIF Data Frame Header

    It parses the header words, eight (or four in legacy mode) 32-bit unsigned integers.

    Args:
        words: Header words, eight (or four) 32-bit unsigned integers.

    Attributes:
        words: Header words, eight (or four) 32-bit unsigned integers.
        frame_length: Length of the frame.
        payload_length: Length of the payload.
        bps: Bits per elementary sample.
        num_ch: Number of channels in the frame.
        num_sample: Number of samples in the frame.
        station_id: Station ID.
            It is either two ASCII ID or a 16-bit integer.
        thread_id: Thread ID.
        version: VDIF version.

    """

    _bit_specs: Dict[str, Sequence[int]] = {
        "seconds": (0, 0, 30),
        "legacy_flag": (0, 30, 1),
        "invalid_flag": (0, 31, 1),
        "frame_index": (1, 0, 24),
        "ref_epoch": (1, 24, 6),
        "frame_length": (2, 0, 24),
        "log2_num_ch": (2, 24, 5),
        "version": (2, 29, 3),
        "station_id": (3, 0, 16),
        "thread_id": (3, 16, 10),
        "bits_per_sample": (3, 26, 5),
        "complex_flag": (3, 31, 1),
    }

    _header_values: Dict[str, int] = {}

    def __init__(self, words: Sequence[int]):
        self.words = words

        for key, val in self._bit_specs.items():
            self._header_values[key] = make_header_parser(*val)(words)

    @property
    def bps(self) -> int:
        """bits per elementary sample
        """
        return self._header_values["bits_per_sample"] + 1

    @property
    def frame_length(self) -> int:
        """length of the frame
        """
        return self._header_values["frame_length"] * 8

    @property
    def payload_length(self) -> int:
        """length of the payload
        """
        return self.frame_length - len(self.words) * 4

    @property
    def num_ch(self) -> int:
        """number of channels in the frame
        """
        return 2 ** self._header_values["log2_num_ch"]

    @property
    def num_sample(self) -> int:
        """number of samples in the frame
        """
        values_per_data_word = 32 // self.bps // (2 if self.is_complex() else 1)
        return self.payload_length // 4 * values_per_data_word // self.num_ch

    @property
    def station_id(self) -> Union[str, int]:
        """station ID

        Note:
            It is either two ASCII ID or a 16-bit integer.
        """
        msb = self._header_values["station_id"] >> 8
        if 48 <= msb <= 128:
            return chr(msb) + chr(self._header_values["station_id"] & 0xFF)
        else:
            return self._header_values["station_id"]

    @property
    def thread_id(self) -> int:
        """thread ID
        """
        return self._header_values["thread_id"]

    @property
    def version(self) -> int:
        """VDIF version
        """
        return self._header_values["version"]

    def is_legacy(self) -> bool:
        """Checks whether the header is legacy or not.

        Return:
            If True, the header is legacy.
        """
        return bool(self._header_values["legacy_flag"])

    def is_complex(self) -> bool:
        """Checks whether the payload is complex data or not.

        Return:
            If True, it is the complex data.
        """
        return bool(self._header_values["complex_flag"])

    def is_valid(self) -> bool:
        """Checks whether the frame is valid or not.

        Return:
            If True, it is valid.
        """
        return bool(self._header_values["invalid_flag"])
