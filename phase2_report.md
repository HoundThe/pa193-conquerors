## PA193 Project - Phase II

Authors: Karel Hajek, Dominik Drdak

### Project design

Project will be split between 2 files - `bench32m.py` and `cli.py`. All the bench32m related functions (encoding, decoding, validation, byte to/from 5-bit group conversion)
will be part of the `bench32m.py`. The command line application will be part of the `cli.py`. This includes accepting commands for bench32m encoding/decoding of arbitrary input or
actual addresses, the input/output processing and transformations. The error handling will be done through the classic Python exception handling, raising exceptions on any invalid
inputs or errorenous situations. We've used `pytest` as the standard testing framework for Python applications, testing mainly on the specification test vectors.

### Current Progress

We're currently supporting encoding of information in correct format into a `bech32m`, decoding of `bech32` or `bech32m` format into 2 parts - human readable part and data. 
We also offer interface for encoding SegWit addresses in `bech32m` format based on the public key and decoding of the addresses. The decoding includes transforming the
5-bit characters back to array of bytes. All of the mentioned functionality includes checks of the format constraints mentioned in the specification. We're able to
pass all of the test vectors mentioned in the `bech32m` specification and we've also created some extra tests for the encoding functions as the specification test
vectors are suitable mostly just for decoding.

### Encountered obstacles

We've encountered a few small obstacles, one of them is understanding the specification and it's purpose as we're unfamiliar with bitcoin and blockchain in general.
Especially regarding support for `bech32m` and `bech32` encoding, if we should support both or only one? Currently we are able to decode both of them, as that is
mandatory part of test vectors, but we are currently encoding only into the `bech32m` format. Other obstacle was the way to deal with and propagate error correction information,
but because it's not part of the test vectors, we've pushed this problem into the next phase. Last obstacle was usage of code from the specification, checksum calculation is specified
using Python code, we didn't find it meaningful to try to "rewrite" the small calculation in a way it doesn't look similar, and used the code from the specification in our code base.
Of course, noting in comments that we took the code from the `bip-0173` specification.


Any of the decisions are still subject to change as we will gain more knowledge on the topic and find potential problems with the decisions in upcoming phase.