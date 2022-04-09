import bech32m
import pytest

BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def base32_to_bytes(b32str: str):
    byte_array = bytearray(len(b32str))

    for idx in range(
        len(b32str)
    ):  # Not very efficient, but I am lazy to create a map for this
        byte_array[idx] = BECH32_CHARSET.index(b32str[idx])

    return bytes(byte_array)


VALID_BECH32M = [
    "A1LQFN3A",
    "a1lqfn3a",
    "an83characterlonghumanreadablepartthatcontainsthetheexcludedcharactersbioandnumber11sg7hg6",
    "abcdef1l7aum6echk45nj3s0wdvt2fg8x9yrzpqzd3ryx",
    "11llllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllludsr8",
    "split1checkupstagehandshakeupstreamerranterredcaperredlc445v",
    "?1v759aa",
]

INVALID_BECH32M = [
    "\x20" + "1xj0phk",
    "\x7F" + "1g6xzxy",
    "\x80" + "1vctc34",
    "an84characterslonghumanreadablepartthatcontainsthetheexcludedcharactersbioandnumber11d6pts4",
    "qyrz8wqd2c9m",
    "1qyrz8wqd2c9m",
    "y1b0jsk6g",
    "lt1igcx5c0",
    "in1muywd",
    "mm1crxm3i",
    "au1s5cgom",
    "M1VUXWEZ",
    "16plkw9",
    "1p2gdwpf",
]

# Custom created test vectors for encoder
# format  (bech32m string, data hexstring)
DECODE_BECH32M_MATCH = [
    ("abcdef140x77khk82w", "abcdef"),
    ("test1wejkxar0wg64ekuu", "766563746f72"),
    ("A1LQFN3A", ""),
    ("a1lqfn3a", ""),
    (
        "an83characterlonghumanreadablepartthatcontainsthetheexcludedcharactersbioandnumber11sg7hg6",
        "",
    ),
    (
        "abcdef1l7aum6echk45nj3s0wdvt2fg8x9yrzpqzd3ryx",
        "ffbbcdeb38bdab49ca307b9ac5a928398a418820",
    ),
    (
        "11llllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllludsr8",
        "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffc0",
    ),
    (
        "split1checkupstagehandshakeupstreamerranterredcaperredlc445v",
        "c5f38b70305f519bf66d85fb6cf03058f3dde463ecd7918f2dc743918f2d",
    ),
    ("?1v759aa", ""),
]


# Custom created test vectors for encoder
# format  (human, data, correct_result)
ENCODE_BECH32M_VALID = [
    ("A", bytes(), "a1lqfn3a"),
    ("a", bytes(), "a1lqfn3a"),
    (
        "an83characterlonghumanreadablepartthatcontainsthetheexcludedcharactersbioandnumber1",
        bytes(),
        "an83characterlonghumanreadablepartthatcontainsthetheexcludedcharactersbioandnumber11sg7hg6",
    ),
    (
        "abcdef",
        base32_to_bytes("l7aum6echk45nj3s0wdvt2fg8x9yrzpq"),
        "abcdef1l7aum6echk45nj3s0wdvt2fg8x9yrzpqzd3ryx",
    ),
    (
        "split",
        base32_to_bytes("checkupstagehandshakeupstreamerranterredcaperred"),
        "split1checkupstagehandshakeupstreamerranterredcaperredlc445v",
    ),
    (
        "?",
        bytes(),
        "?1v759aa",
    ),
    (
        "test",
        bech32m.encode_data(bytes.fromhex("766563746f72")),
        "test1wejkxar0wg64ekuu",
    ),
    (
        "an83characterlonghumanreadablepartthatcontainsthetheexcludedcharactersbioandnumber1",
        bech32m.encode_data(bytes.fromhex("")),
        "an83characterlonghumanreadablepartthatcontainsthetheexcludedcharactersbioandnumber11sg7hg6",
    ),
    (
        "abcdef",
        base32_to_bytes("l7aum6echk45nj3s0wdvt2fg8x9yrzpq"),
        "abcdef1l7aum6echk45nj3s0wdvt2fg8x9yrzpqzd3ryx",
    ),
    (
        "split",
        base32_to_bytes("checkupstagehandshakeupstreamerranterredcaperred"),
        "split1checkupstagehandshakeupstreamerranterredcaperredlc445v",
    ),
]


ENCODE_BECH32M_INVALID = [
    (chr(0x20), bytes()),
    (chr(0x7F), bytes()),
    (chr(0x80), bytes()),
    (
        "an84characterslonghumanreadablepartthatcontainsthetheexcludedcharactersbioandnumber1",
        bytes(),
    ),
    ("", base32_to_bytes("qyrz8w")),
    ("", base32_to_bytes("")),
    ("", base32_to_bytes("p")),
]


def test_bech32m_encode_valid():
    for human, data, result in ENCODE_BECH32M_VALID:
        assert bech32m.encode(human, bech32m.decode_data(data)) == result


def test_bech32m_encode_invalid():
    for human, data in ENCODE_BECH32M_INVALID:
        with pytest.raises(Exception):
            bech32m.encode(human, data)


def test_bech32m_decode_valid():
    for string in VALID_BECH32M:
        try:
            bech32m.decode(string)
        except Exception as ex:
            assert False, f"Exception raised - {ex}"


def test_bech32m_decode_match():
    for string, ref in DECODE_BECH32M_MATCH:
        try:
            result = bech32m.decode(string)
            assert result[1].hex() == ref
        except Exception as ex:
            assert False, f"Exception raised - {ex}"


def test_bech32m_decode_invalid():
    for string in INVALID_BECH32M:
        with pytest.raises(Exception):
            bech32m.decode(string)
