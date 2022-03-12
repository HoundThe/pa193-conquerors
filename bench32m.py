BECH32_PROTOCOL = 0
BECH32M_PROTOCOL = 1

BECH32_XOR = 1
BECH32M_XOR = 0x2BC830A3

BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def bech32_polymod(values) -> int:
    """Code taken from the bip-0173 bech32 specification"""
    GEN = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for v in values:
        b = chk >> 25
        chk = (chk & 0x1FFFFFF) << 5 ^ v
        for i in range(5):
            chk ^= GEN[i] if ((b >> i) & 1) else 0
    return chk


def bech32_hrp_expand(s: str) -> bytes:
    """Code taken from the bip-0173 bech32 specification"""
    return bytes([ord(x) >> 5 for x in s] + [0] + [ord(x) & 31 for x in s])


def bech32_verify_checksum(hrp: str, data: bytes):
    """Code taken from the bip-0173 bech32 specification"""
    return bech32_polymod(bech32_hrp_expand(hrp) + data) == 1


def create_checksum(hrp: str, data: bytes, protocol) -> bytes:
    """Code based on the bip-0173 bech32 specification"""
    values = bech32_hrp_expand(hrp) + data
    xor_const = BECH32_XOR if protocol == BECH32_PROTOCOL else BECH32M_XOR
    polymod = bech32_polymod(values + bytes([0, 0, 0, 0, 0, 0])) ^ xor_const
    return bytes([(polymod >> 5 * (5 - i)) & 31 for i in range(6)])


def check_protocol(protocol):
    if protocol != BECH32_PROTOCOL and protocol != BECH32M_PROTOCOL:
        raise ValueError("Incorrect protocol value")


def check_human(human: str):
    if len(human) < 1 or len(human) > 83:
        raise ValueError("Human part length has to be in range [1-83]")

    for char in human:
        if ord(char) < 33 or ord(char) > 126:
            raise ValueError(
                "Human part character out of range, acceptable range is [33-126]"
            )


def check_data(data: bytes) -> bool:
    for value in data:
        # Each value of data has to fit in 5 bits
        if value < 0 or value > 31:
            raise ValueError(
                "data is containing values out of range. Valid values are [0-31]"
            )


def encode(human: str, data: bytes, protocol) -> str:
    check_protocol(protocol)
    check_human(human)
    check_data(data)

    # Bech32 string has max length of 90, 6 is the checksum length
    if len(human) + len("1") + len(data) + 6 > 90:
        raise ValueError("Bech32 string is too long, maximum length is 90")

    # Human needs to be lowercase for checksum calculation
    # Encoder also always output lowercase
    human = human.lower()

    # Format = | Human readable part | 1 | data + checksum(data)
    data_part = data + create_checksum(human, data, protocol)
    return human + "1" + "".join(BECH32_CHARSET[i] for i in data_part)


def decode(string: str):
    pass


def address_encode(pubkey: str):
    pass


def address_decode(address: str):
    pass


# res = encode("a", [], BECH32_PROTOCOL)
# print(res)
