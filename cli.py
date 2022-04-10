#! /bin/env python3

import argparse
from io import BufferedReader, BufferedWriter
import sys
import os
from enum import Enum
import base64
from typing import IO, Any
import bech32m


class DataFormat(Enum):
    TEXT = "text"
    HEX = "hex"
    BINARY = "binary"
    BASE64 = "base64"


def read_bytes(file: BufferedReader, form: DataFormat) -> bytes:
    if form == DataFormat.HEX:
        data = bytes.fromhex(file.read().decode("utf-8"))
    elif form == DataFormat.BINARY:
        data = file.read()
    elif form == DataFormat.BASE64:
        data = base64.decodebytes(file.read())

    return data


def write_bytes(file: IO[Any], data: bytes, form: DataFormat) -> None:
    if form == DataFormat.HEX:
        file.write(data.hex().encode("ascii"))
    elif form == DataFormat.BINARY:
        file.write(data)
    elif form == DataFormat.BASE64:
        file.write(base64.encodebytes(data))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Bech32m encoder/decoder of arbitrary input"
    )
    parser.add_argument(
        "-e", "--encode", action="store_true", help="if you want to encode"
    )
    parser.add_argument(
        "-d",
        "--decode",
        action="store_true",
        help="if you want to decode, by default encoding is assumed.",
    )
    parser.add_argument(
        "-i",
        "--input-path",
        action="store",
        type=str,
        help="path to the input file, if no path specified, stdin is used unless --data argument is used.",
    )
    parser.add_argument(
        "-inform",
        "--input-format",
        action="store",
        type=str,
        choices=["base64", "hex", "binary"],
        default="hex",
        help="format of the input bytes if encoding. Default used is hex.",
    )
    parser.add_argument(
        "-o",
        "--output-path",
        action="store",
        type=str,
        help="path to the output file, if no path specified, stdout is used.",
    )
    parser.add_argument(
        "-outform",
        "--output-format",
        action="store",
        type=str,
        choices=["base64", "hex", "binary"],
        default="hex",
        help="format of the output when decoding. Default used is hex.",
    )
    parser.add_argument(
        "-hrp",
        "--human-part",
        action="store",
        type=str,
        default="default_hrp",
        help="human readable part of the bech32m encoded string. Used only when encoding.",
    )
    parser.add_argument(
        "--data",
        action="store",
        type=str,
        help="option to pass text data as an argument instead of using file or stdin. If the data is used for encoding, the text is encoded using utf-8.",
    )

    args = parser.parse_args()

    # Encoding is default behavior
    to_encode = not args.decode

    if args.input_path and args.data:
        raise ValueError("Two data input sources specified")

    # Raises on invalid human readable string
    bech32m.check_human(args.human_part)

    # Dataformat should be always correct enum, constraint on format is in argparse
    # Format specifier is used for byte-like data -> input when encoding, output when decoding
    inform = DataFormat(args.input_format)
    outform = DataFormat(args.output_format)

    input_data = args.data

    # Prefer data argument over default stdin
    if args.data and to_encode:
        input_data = input_data.encode("utf8")
    # If not passed through argument, read file or stdin
    elif not args.data:
        if to_encode:
            # With encoding, the input are bytes and can be binary
            with open(args.input_path, "rb") if args.input_path else os.fdopen(
                sys.stdin.fileno(), "rb"
            ) as infile:
                input_data = read_bytes(infile, inform)
        else:
            # With decoding, the input is bech32m string, so a valid text
            with open(args.input_path, "r") if args.input_path else os.fdopen(
                sys.stdin.fileno(), "r"
            ) as infile:
                input_data = infile.read().strip()

    # input_data should be str if we are decoding, otherwise bytes

    result = bytes()

    if to_encode:
        result = bech32m.encode(args.human_part, input_data)
    else:
        result = bech32m.decode(input_data)[1]

    # Maybe removing the output file on exception?
    OUTFLAGS = "w" if to_encode else "wb"

    with open(args.output_path, OUTFLAGS) if args.output_path else os.fdopen(
        sys.stdout.fileno(), OUTFLAGS, closefd=False
    ) as outfile:
        if to_encode:
            print(result, file=outfile)
        else:
            write_bytes(outfile, result, outform)
