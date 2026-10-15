# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
import argparse
from pathlib import Path
import sys

FEATURES = (
    "Embedded Wallet Support",
    "Plugin Architecture",
    "React Native Support",
    "Improved Evals & Benchmarks",
    "Token Plugin",
    "NFT Plugin",
    "DeFi Plugin",
    "Misc Plugin",
    "Blinks Plugin",
)


def main():
    parser = argparse.ArgumentParser(
        description="List documented Solana Agent Kit v2 feature names in a saved text file."
    )
    parser.add_argument("file", help="Path to a UTF-8 text file containing the saved overview")
    args = parser.parse_args()

    try:
        text = Path(args.file).read_text(encoding="utf-8")
    except FileNotFoundError:
        print("error: input file not found", file=sys.stderr)
        return 2
    except (OSError, UnicodeError) as exc:
        print(f"error: cannot read UTF-8 input ({exc})", file=sys.stderr)
        return 2

    found = [name for name in FEATURES if name.casefold() in text.casefold()]
    if not found:
        print("No listed feature names found.")
    else:
        for name in found:
            print(name)
    return 0


if __name__ == "__main__":
    sys.exit(main())