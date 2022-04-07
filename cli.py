import argparse
import sys
from enum import Enum
import bech32m

description = "Bech32m encoder/decoder of variable input"


class DataFormat(Enum):
    HEX = "hex"
    BINARY = "binary"
    BASE64 = "base64"


def read_data(file, format) -> bytes:
    pass


def write_data(file, format) -> None:
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-e", "--encode", action="store_true", help="if you want to encode"
    )
    parser.add_argument(
        "-d",
        "--decode",
        action="store_true",
        help="if you want to decode, by default encoding is assumed",
    )
    parser.add_argument(
        "-i",
        "--input-path",
        action="store",
        nargs=1,
        type=str,
        help="path to the input file, if no path specified, stdin is used",
    )
    parser.add_argument(
        "-inform",
        "--input-format",
        action="store",
        nargs=1,
        type=str,
        choices=["base64", "hex", "binary"],
        help="format of the input, allowed are: base64, hex, binary. Default used is binary",
    )
    parser.add_argument(
        "-o",
        "--output-path",
        action="store",
        nargs=1,
        type=str,
        help="path to the output file, if no path specified, stdout is used",
    )
    parser.add_argument(
        "-outform",
        "--output-format",
        action="store",
        nargs=1,
        type=str,
        choices=["base64", "hex", "binary"],
        help="format of the output, allowed are: base64, hex, binary. Default used is binary",
    )

    args = parser.parse_args()

    to_encode = False if args.decode else True

    infile = open(args.input_path) if args.input_path else sys.stdin
    outfile = open(args.input_path) if args.input_path else sys.stdout

    data = read_data()

    result = bytes()

    if to_encode:
        result = bech32m.encode("", data)
    else:
        result = bech32m.decode("", data)

    write_data(result)
