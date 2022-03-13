import bench32m
import pytest
import binascii

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

VALID_SEGWIT_ADDRESS = [
    [
        "BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4",
        "0014751e76e8199196d454941c45d1b3a323f1433bd6",
    ],
    [
        "tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sl5k7",
        "00201863143c14c5166804bd19203356da136c985678cd4d27a1b8c6329604903262",
    ],
    [
        "bc1pw508d6qejxtdg4y5r3zarvary0c5xw7kw508d6qejxtdg4y5r3zarvary0c5xw7kt5nd6y",
        "5128751e76e8199196d454941c45d1b3a323f1433bd6751e76e8199196d454941c45d1b3a323f1433bd6",
    ],
    ["BC1SW50QGDZ25J", "6002751e"],
    ["bc1zw508d6qejxtdg4y5r3zarvaryvaxxpcs", "5210751e76e8199196d454941c45d1b3a323"],
    [
        "tb1qqqqqp399et2xygdj5xreqhjjvcmzhxw4aywxecjdzew6hylgvsesrxh6hy",
        "0020000000c4a5cad46221b2a187905e5266362b99d5e91c6ce24d165dab93e86433",
    ],
    [
        "tb1pqqqqp399et2xygdj5xreqhjjvcmzhxw4aywxecjdzew6hylgvsesf3hn0c",
        "5120000000c4a5cad46221b2a187905e5266362b99d5e91c6ce24d165dab93e86433",
    ],
    [
        "bc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqzk5jj0",
        "512079be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798",
    ],
]

INVALID_SEGWIT_ADDRESS = [
    "tc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vq5zuyut",
    "bc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqh2y7hd",
    "tb1z0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqglt7rf",
    "BC1S0XLXVLHEMJA6C4DQV22UAPCTQUPFHLXM9H8Z3K2E72Q4K9HCZ7VQ54WELL",
    "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kemeawh",
    "tb1q0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vq24jc47",
    "bc1p38j9r5y49hruaue7wxjce0updqjuyyx0kh56v8s25huc6995vvpql3jow4",
    "BC130XLXVLHEMJA6C4DQV22UAPCTQUPFHLXM9H8Z3K2E72Q4K9HCZ7VQ7ZWS8R",
    "bc1pw5dgrnzv",
    "bc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7v8n0nx0muaewav253zgeav",
    "BC1QR508D6QEJXTDG4Y5R3ZARVARYV98GJ9P",
    "tb1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vq47Zagq",
    "bc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7v07qwwzcrf",
    "tb1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vpggkg4j",
    "bc1gmk9yu",
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
        "1",
        base32_to_bytes(
            "llllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll"
        ),
        "11llllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllludsr8",
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
        assert bench32m.encode(human, data) == result


def test_bech32m_encode_invalid():
    for human, data in ENCODE_BECH32M_INVALID:
        with pytest.raises(Exception):
            bench32m.encode(human, data)


def test_bech32m_decode_valid():
    for string in VALID_BECH32M:
        try:
            bench32m.decode(string)
        except Exception as ex:
            assert False, f"Exception raised - {ex}"


def test_bech32m_decode_invalid():
    for string in INVALID_BECH32M:
        with pytest.raises(Exception):
            bench32m.decode(string)


def test_bech32m_decode_address_invalid():
    for string in INVALID_SEGWIT_ADDRESS:
        with pytest.raises(Exception):
            bench32m.address_decode(string)


def segwit_scriptpubkey(ver, prog):
    """Construct a Segwit scriptPubKey for a given witness program."""
    return bytes([ver + 0x50 if ver else 0, len(prog)]) + prog


def test_bech32m_decode_address_valid():
    for input, output in VALID_SEGWIT_ADDRESS:
        try:
            human, ver, program = bench32m.address_decode(input)
            result = segwit_scriptpubkey(ver, program)
            assert result == binascii.unhexlify(output)
        except Exception as ex:
            assert False, f"Exception raised - {ex}"


VALID_SEGWIT_ADDRESS_BECH32M = [
    [
        "bc1pw508d6qejxtdg4y5r3zarvary0c5xw7kw508d6qejxtdg4y5r3zarvary0c5xw7kt5nd6y",
        "5128751e76e8199196d454941c45d1b3a323f1433bd6751e76e8199196d454941c45d1b3a323f1433bd6",
    ],
    ["BC1SW50QGDZ25J", "6002751e"],
    [
        "bc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqzk5jj0",
        "512079be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798",
    ],
]

VALID_SEGWIT_ADDRESS_BECH32 = [
    [
        "BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4",
        "0014751e76e8199196d454941c45d1b3a323f1433bd6",
    ],
    [
        "tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sl5k7",
        "00201863143c14c5166804bd19203356da136c985678cd4d27a1b8c6329604903262",
    ],
]


def test_bech32m_encode_address_valid():
    for output, input in VALID_SEGWIT_ADDRESS_BECH32M:
        witver = input[:2]
        if witver != "00":
            witver = str(int(witver) - 50)
        try:
            assert bench32m.address_encode(output[:2], witver, input[4:]) == output.lower()
        except Exception as ex:
            assert False, f"Exception raised - {ex}"
