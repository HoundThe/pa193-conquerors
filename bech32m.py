from typing import Tuple, Union

BECH32M = 0x2BC830A3

BECH32M_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
BECH32M_MAX_LENGTH = 90
BECH32M_CHECKSUM_LENGTH = 6


def polymod(values: bytes) -> int:
    """Code taken from the bip-0350 bech32m specification"""
    GEN = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for v in values:
        b = chk >> 25
        chk = (chk & 0x1FFFFFF) << 5 ^ v
        for i in range(5):
            chk ^= GEN[i] if ((b >> i) & 1) else 0
    return chk


def hrp_expand(s: Union[str, list[str]]) -> bytes:
    """Code taken from the bip-0350 bech32m specification"""
    return bytes([ord(x) >> 5 for x in s] + [0] + [ord(x) & 31 for x in s])


def verify_checksum(hrp: Union[str, list[str]], data: bytes) -> Union[int, None]:
    """Code taken from the bip-0350 bech32m specification"""
    check = polymod(hrp_expand(hrp) + data)
    if check != BECH32M:
        return None
    return check


def create_checksum(hrp: str, data: bytes) -> bytes:
    """Code based on the bip-0350 bech32m specification"""
    values = hrp_expand(hrp) + data
    mod = polymod(values + bytes([0, 0, 0, 0, 0, 0])) ^ BECH32M
    return bytes([(mod >> 5 * (5 - i)) & 31 for i in range(6)])


def check_human(human: str) -> None:
    if len(human) < 1 or len(human) > 83:
        raise ValueError(
            f"Human-readable part length has to be in range [1-83], but is {len(human)}"
        )

    if any(True for char in human if ord(char) < 33 or ord(char) > 126):
        raise ValueError(
            "Human-readable part character out of range, acceptable range is [33-126]"
        )


def base32_to_bytes(b32str: str) -> bytes:
    byte_array = bytearray(len(b32str))

    for idx, _ in enumerate(b32str):
        byte_array[idx] = BECH32M_CHARSET.index(b32str[idx])

    return bytes(byte_array)


def encode(human: str, raw_data: bytes) -> str:
    check_human(human)

    data = encode_data(raw_data)

    # Bech32 string has max length of 90
    strlen = len(human) + len("1") + len(data) + BECH32M_CHECKSUM_LENGTH
    if strlen > BECH32M_MAX_LENGTH:
        raise ValueError(f"Bech32 string is too long ({strlen}), maximum length is 90")

    # Human needs to be lowercase for checksum calculation
    # Encoder also always output lowercase
    human = human.lower()

    # Format = | Human readable part | 1 | data + checksum(data)
    data_part = data + create_checksum(human, data)
    return human + "1" + "".join(BECH32M_CHARSET[i] for i in data_part)


def detect_single_error(hrp: str, data_bytes: bytes) -> Union[str, None]:
    """Naive detection off single character error

    Task:
    "it suffices to implement a simplified
    error detection that is able to identify just a _single_ symbol error in the
    encoded string and suggest the correct input. This implementation can be done
    naively by iterating over the possible choices and can be an optional feature in
    case the input string is too large."

        returns corrected string if found or None
    """

    human_part = list(hrp)
    data_part = bytearray(data_bytes)

    # First start with data
    for i, _ in enumerate(data_part):
        for j, _ in enumerate(BECH32M_CHARSET):
            data_part[i] = j
            # Check if the string got fixed
            is_valid = verify_checksum(human_part, data_part)
            if is_valid:
                return (
                    "".join(human_part)
                    + "1"
                    + "".join(BECH32M_CHARSET[i] for i in data_part)
                )

            # Else return back the original value
            data_part[i] = data_bytes[i]

    # If data part didn't have the error, human part could
    for i, _ in enumerate(hrp):
        for j in range(33, 126):
            human_part[i] = chr(j)
            # Check if the string got fixed
            is_valid = verify_checksum(human_part, data_part)
            if is_valid:
                return (
                    "".join(human_part)
                    + "1"
                    + "".join(BECH32M_CHARSET[i] for i in data_part)
                )

            # Else return back the original value
            human_part[i] = hrp[i]

    return None


def decode(string: str) -> Tuple[str, bytes, int]:
    if "1" not in string:
        raise ValueError("Missing separator '1'")

    if len(string) > BECH32M_MAX_LENGTH:
        raise ValueError("Bech32 string is too long, maximum length is 90")

    if string.upper() != string and string.lower() != string:
        raise ValueError("String has mixed upper and lower case, maybe a typo?")

    string = string.lower()

    human, data = string.rsplit("1", maxsplit=1)

    # Check if there are only valid bech32m characters,
    # if yes the data values are valid
    if not all(True for x in data if x in BECH32M_CHARSET):
        raise ValueError()

    if len(data) < BECH32M_CHECKSUM_LENGTH:
        raise ValueError("Checksum is too short")

    data_bytes = base32_to_bytes(data)
    check_human(human)

    enc = verify_checksum(human, data_bytes)
    if not enc:
        is_fixable = detect_single_error(human, data_bytes)
        if is_fixable:
            raise ValueError(
                f"The string is not valid, did you mean to use '{is_fixable}' instead?"
            )
        raise ValueError(
            "The string is not valid and it contains more than one incorrect character."
        )

    return (human, decode_data(data_bytes[:-BECH32M_CHECKSUM_LENGTH]), enc)


def decode_data(data: bytes) -> bytes:
    decoded_bytes = bytearray()
    reg = 0
    stored_bits = 0

    for byte in data:
        # We need to hold at most 12 bits
        reg = ((reg << 5) | byte) & 0xFFF
        stored_bits += 5  # We've read 5 bits
        if stored_bits >= 8:  # If we have enough bits to save
            stored_bits -= 8
            # Shift it to start and take only the complete 8 bits
            decoded_bytes.append((reg >> stored_bits) & 0xFF)

    # Padd the data if there is an incomplete byte from the LSB side
    if stored_bits > 0 and (reg << (8 - stored_bits)) & 0xFF != 0:
        decoded_bytes.append((reg << (8 - stored_bits)) & 0xFF)

    return bytes(decoded_bytes)


def encode_data(data: bytes) -> bytes:
    encoded_bytes = bytearray()
    reg = 0
    stored_bits = 0

    for byte in data:
        # We need to hold at most 12 bits
        reg = ((reg << 8) | byte) & 0xFFF
        stored_bits += 8  # We've read 8 bits
        while stored_bits >= 5:  # Write all 5 bit groups
            stored_bits -= 5
            encoded_bytes.append((reg >> stored_bits) & 0x1F)

    # If there are any leftovers, padd them to 5 bit group
    if stored_bits != 0 and (reg << (5 - stored_bits)) & 0x1F != 0:
        encoded_bytes.append((reg << (5 - stored_bits)) & 0x1F)

    return bytes(encoded_bytes)
