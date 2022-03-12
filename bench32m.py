BECH32_PROTOCOL = 0
BECH32M_PROTOCOl = 1

BECH32_XOR = 1
BECH32M_XOR = 0x2BC830A3

BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def bech32_polymod(values):
    """Code taken from the bip-0173 bech32 specification"""
    GEN = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for v in values:
        b = chk >> 25
        chk = (chk & 0x1FFFFFF) << 5 ^ v
        for i in range(5):
            chk ^= GEN[i] if ((b >> i) & 1) else 0
    return chk


def bech32_hrp_expand(s: str) -> list[int]:
    """Code taken from the bip-0173 bech32 specification"""
    return [ord(x) >> 5 for x in s] + [0] + [ord(x) & 31 for x in s]


def bech32_verify_checksum(hrp, data):
    """Code taken from the bip-0173 bech32 specification"""
    return bech32_polymod(bech32_hrp_expand(hrp) + data) == 1


def create_checksum(hrp, data, protocol):
    """Code based on the bip-0173 bech32 specification"""
    values = bech32_hrp_expand(hrp) + data
    xor_const = BECH32_XOR if protocol == BECH32_PROTOCOL else BECH32M_XOR
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ xor_const
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]


def encode(human: str, data: list[int], protocol) -> str:
    # TODO validate human, data, protocol (correct format, length, values)

    # Human needs to be lowecase when calculating checksum!!
    # Encoder always outputs lowercase Bech32 string

    # Data is in format list of values of [0, 31] - 5 bits of information each,
    # This will get mapped to the charset of 32 characters

    # Format = | Human readable part | 1 | data + checksum(data)

    data_part = data + create_checksum(human, data, protocol)
    return human + "1" + "".join(BECH32_CHARSET[i] for i in data_part)


def decode(string: str):
    pass


def address_encode(pubkey: str):
    pass


def address_decode(address: str):
    pass
