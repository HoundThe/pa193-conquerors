import cli
import pytest
import subprocess


"""
usage: cli.py [-h] [-e] [-d] [-i INPUT_PATH] [-inform {base64,hex,binary}] [-o OUTPUT_PATH] [-outform {base64,hex,binary}] [-hrp HUMAN_PART] [--data DATA]

Bech32m encoder/decoder of arbitrary input

optional arguments:
  -h, --help            show this help message and exit
  -e, --encode          if you want to encode
  -d, --decode          if you want to decode, by default encoding is assumed.
  -i INPUT_PATH, --input-path INPUT_PATH
                        path to the input file, if no path specified, stdin is used unless --data argument is used.
  -inform {base64,hex,binary}, --input-format {base64,hex,binary}
                        format of the input bytes if encoding. Default used is hex.
  -o OUTPUT_PATH, --output-path OUTPUT_PATH
                        path to the output file, if no path specified, stdout is used.
  -outform {base64,hex,binary}, --output-format {base64,hex,binary}
                        format of the output when decoding. Default used is hex.
  -hrp HUMAN_PART, --human-part HUMAN_PART
                        human readable part of the bech32m encoded string. Used only when encoding.
  --data DATA           option to pass text data as an argument instead of using file or stdin. If the data is used for encoding, the text is encoded using utf-8.
"""


def test_encode_too_long_data():
    with pytest.raises(subprocess.SubprocessError):
        subprocess.check_output(
            [
                "python3",
                "cli.py",
                "--data",
                "asdaasdasd$#%#W@!@sdasdasasdsadasdsaasda123s1TOOLONG",
            ],
            text=True,
            timeout=10,
        )


def test_encode_non_ascii_data_char():
    subprocess.check_output(
        [
            "python3",
            "cli.py",
            "--data",
            "😀	$#%#W@!@sdasdasasdsadasdsaasda123s1",
        ],
        text=True,
        timeout=10,
    )


def test_encode_non_ascii_hrp():
    with pytest.raises(subprocess.SubprocessError):
        subprocess.check_output(
            [
                "python3",
                "cli.py",
                "--data",
                "😀	$#sadasdsaasda123s1",
                "-hrp",
                "😀",
            ],
            text=True,
            timeout=10,
        )


def test_encode_too_long_hrp():
    with pytest.raises(subprocess.SubprocessError):
        subprocess.check_output(
            [
                "python3",
                "cli.py",
                "--data",
                "😀	$#sadasdsaasda123s1",
                "-hrp",
                "adsasdasdsadsadasddasadsadsasdsadasdsdsaddsaasddasdasdsads",
            ],
            text=True,
            timeout=10,
        )


def test_encode_binary1():
    result = subprocess.check_output(
        [
            "python3",
            "cli.py",
            "-i",
            "tests/inputs/encode_input.bin",
            "-inform",
            "binary",
        ],
        text=True,
        timeout=10,
    )

    assert (
        result.rstrip() == "default_hrp1a7lmmmalhhhml000h777l0aaa7lmmmalhhhml0g32000c"
    )


def test_encode_binary2():
    result = subprocess.check_output(
        [
            "python3",
            "cli.py",
            "-i",
            "tests/inputs/encode_input.bin",
            "-inform",
            "binary",
            "-hrp",
            "kappa123",
        ],
        text=True,
        timeout=10,
    )

    assert result.rstrip() == "kappa1231a7lmmmalhhhml000h777l0aaa7lmmmalhhhml0g8agt48"


def test_encode_binary3():
    result = subprocess.check_output(
        [
            "python3",
            "cli.py",
            "-i",
            "tests/inputs/encode_input.hex",
            "-inform",
            "binary",
            "-hrp",
            "kappa123",
        ],
        text=True,
        timeout=10,
    )

    assert result.rstrip() == "kappa1231venxvenxvenxvenxvenxvenxvck54jh6"


def test_encode_hex():
    result = subprocess.check_output(
        [
            "python3",
            "cli.py",
            "-i",
            "tests/inputs/encode_input.hex",
            "-inform",
            "hex",
            "-hrp",
            "kappa123",
        ],
        text=True,
        timeout=10,
    )

    assert result.rstrip() == "kappa1231llllllllllll7ceyt6k"


def test_encode_b64():
    result = subprocess.check_output(
        [
            "python3",
            "cli.py",
            "-i",
            "tests/inputs/encode_input.b64",
            "-inform",
            "base64",
            "-hrp",
            "kappa123",
        ],
        text=True,
        timeout=10,
    )

    assert result.rstrip() == "kappa1231venxvenxvenxvenxvenxvenxvck54jh6"


def test_encode_b64():
    result = subprocess.check_output(
        [
            "python3",
            "cli.py",
            "-i",
            "tests/inputs/encode_input.b64",
            "-inform",
            "base64",
            "-hrp",
            "kappa123",
        ],
        text=True,
        timeout=10,
    )

    assert result.rstrip() == "kappa1231venxvenxvenxvenxvenxvenxvck54jh6"


def test_encode_b64_stdin():
    result = subprocess.check_output(
        [
            "python3",
            "cli.py",
            "-inform",
            "base64",
            "-hrp",
            "kappa123",
        ],
        stdin=open("tests/inputs/encode_input.b64", "r"),
        text=True,
        timeout=10,
    )

    assert result.rstrip() == "kappa1231venxvenxvenxvenxvenxvenxvck54jh6"


def test_decode_b64():
    result = subprocess.check_output(
        [
            "python3",
            "cli.py",
            "-i",
            "tests/inputs/decode_input.b64",
            "-outform",
            "base64",
            "-hrp",
            "kappa123",
            "-d",
        ],
        text=True,
        timeout=10,
    )

    assert result == "ZmZmZmZmZmZmZmZmZmZmZg==\n"


def test_decode_bin():
    result = subprocess.check_output(
        [
            "python3",
            "cli.py",
            "-i",
            "tests/inputs/decode_input.bin",
            "-outform",
            "binary",
            "-hrp",
            "kappa123",
            "-d",
        ],
        timeout=10,
    )

    assert result == bytes.fromhex(
        "EF BF BD EF BF BD EF BF BD EF BF BD EF BF BD EF BF BD EF BF BD EF BF BD"
    )


def test_decode_hex():
    result = subprocess.check_output(
        [
            "python3",
            "cli.py",
            "-i",
            "tests/inputs/decode_input.hex",
            "-outform",
            "hex",
            "-hrp",
            "kappa123",
            "-d",
        ],
        timeout=10,
        text=True,
    )

    assert result.rstrip() == "ffffffffffffffff"


def test_decode_hex_stdin():
    result = subprocess.check_output(
        [
            "python3",
            "cli.py",
            "-i",
            "tests/inputs/decode_input.hex",
            "-outform",
            "hex",
            "-hrp",
            "kappa123",
            "-d",
        ],
        stdin=open("tests/inputs/decode_input.hex", "r"),
        timeout=10,
        text=True,
    )

    assert result.rstrip() == "ffffffffffffffff"
