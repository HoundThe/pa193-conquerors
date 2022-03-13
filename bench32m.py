from typing import Tuple

BECH32 = 1
BECH32M = 0x2BC830A3

BECH32M_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
BECH32M_MAX_LENGTH = 90
BECH32M_CHECKSUM_LENGTH = 6


def bech32_polymod(values) -> int:
    """Code taken from the bip-0350 bech32m specification"""
    GEN = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for v in values:
        b = chk >> 25
        chk = (chk & 0x1FFFFFF) << 5 ^ v
        for i in range(5):
            chk ^= GEN[i] if ((b >> i) & 1) else 0
    return chk


def bech32_hrp_expand(s: str) -> bytes:
    """Code taken from the bip-0350 bech32m specification"""
    return bytes([ord(x) >> 5 for x in s] + [0] + [ord(x) & 31 for x in s])


def bech32_verify_checksum(hrp: str, data: bytes):
    """Code taken from the bip-0350 bech32m specification"""
    check = bech32_polymod(bech32_hrp_expand(hrp) + data)
    if check not in [BECH32, BECH32M]:
        return None
    return check


def create_checksum(hrp: str, data: bytes) -> bytes:
    """Code based on the bip-0350 bech32m specification"""
    values = bech32_hrp_expand(hrp) + data
    polymod = bech32_polymod(values + bytes([0, 0, 0, 0, 0, 0])) ^ BECH32M
    return bytes([(polymod >> 5 * (5 - i)) & 31 for i in range(6)])


def check_human(human: str):
    if len(human) < 1 or len(human) > 83:
        raise ValueError("Human part length has to be in range [1-83]")

    if any(True for char in human if ord(char) < 33 or ord(char) > 126):
        raise ValueError(
            "Human part character out of range, acceptable range is [33-126]"
        )


def check_data_values(data: bytes) -> bool:
    if any(True for val in data if val < 0 or val > 31):
        raise ValueError(
            "Data is containing values out of range. Valid values are [0-31]"
        )


def base32_to_bytes(b32str: str):
    byte_array = bytearray(len(b32str))

    for idx in range(
        len(b32str)
    ):  # Not very efficient, but I am lazy to create a map for this
        byte_array[idx] = BECH32M_CHARSET.index(b32str[idx])

    return bytes(byte_array)


def encode(human: str, data: bytes) -> str:
    check_human(human)
    check_data_values(data)

    # Bech32 string has max length of 90
    if len(human) + len("1") + len(data) + BECH32M_CHECKSUM_LENGTH > BECH32M_MAX_LENGTH:
        raise ValueError("Bech32 string is too long, maximum length is 90")

    # Human needs to be lowercase for checksum calculation
    # Encoder also always output lowercase
    human = human.lower()

    # Format = | Human readable part | 1 | data + checksum(data)
    data_part = data + create_checksum(human, data)
    return human + "1" + "".join(BECH32M_CHARSET[i] for i in data_part)


def decode(string: str) -> Tuple[str, bytes, int]:
    if "1" not in string:
        raise ValueError("Missing separator '1'")

    if len(string) > BECH32M_MAX_LENGTH:
        raise ValueError("Bech32 string is too long, maximum length is 90")

    if string.upper() != string and string.lower() != string:
        raise ValueError("Error has mixed upper and lower case")

    string = string.lower()

    human, data = string.rsplit("1", maxsplit=1)

    if not all(True for x in data if x in BECH32M_CHARSET):
        raise ValueError()

    if len(data) < BECH32M_CHECKSUM_LENGTH:
        raise ValueError("Checksum is too short")

    data_bytes = base32_to_bytes(data)

    check_data_values(data_bytes)
    check_human(human)

    enc = bech32_verify_checksum(human, data_bytes)
    if not enc:  # TODO add missing error detection/correction
        raise ValueError("Checksum doesn't match")

    return (human, data_bytes[:-BECH32M_CHECKSUM_LENGTH], enc)


def address_encode(pubkey: str):
    pass


def decode_program(data: bytes):
    all_bytes = bytearray()
    reg = 0
    stored_bits = 0

    for byte in data:
        # We need to hold at most 12 bits
        reg = ((reg << 5) | byte) & 0xFFF
        stored_bits += 5  # We've read 5 bits
        if stored_bits >= 8:  # If we have enough bits to save
            stored_bits -= 8
            # Shift it to start and take only the complete 8 bits
            all_bytes.append((reg >> stored_bits) & 0xFF)

    # Any incomplete group at the end MUST be 4 bits or less,
    # MUST be all zeroes, and is discarded.
    # Second or part is - shift out any non-stored bits in byte, check if 0
    if stored_bits > 4 or (reg << (8 - stored_bits)) & 0xFF:
        raise ValueError("Invalid witness program")

    return bytes(all_bytes)


def address_decode(address: str) -> Tuple[str, int, bytes]:
    human, data, enc = decode(address)

    if len(data) < 3:
        raise ValueError("Invalid data length")

    if human not in ["bc", "tb"]:
        raise ValueError("Readable part of SegWit address has to be 'tb' or 'bc'")

    ver = data[0]
    if ver < 0 or ver > 16:
        raise ValueError("Invalid version value, has to be in range [0-16]")

    program = decode_program(data[1:])
    if len(program) < 2 or len(program) > 40:
        raise ValueError("Invalid program length")

    if ver == 0 and len(program) != 20 and len(program) != 32:
        raise ValueError("Invalid program length for version 0")

    if (ver == 0 and enc != BECH32) or (ver != 0 and enc != BECH32M):
        raise ValueError("Invalid encoding based on version")

    return (human, ver, program)
