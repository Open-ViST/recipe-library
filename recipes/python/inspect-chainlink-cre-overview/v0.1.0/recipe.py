# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
import argparse
import pathlib
import re
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Print CRE concepts found in a local documentation text file."
    )
    parser.add_argument("input", help="Path to a saved, UTF-8 documentation text file")
    args = parser.parse_args()

    path = pathlib.Path(args.input)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2
    except (OSError, UnicodeError) as exc:
        print(f"error: cannot read UTF-8 input: {exc}", file=sys.stderr)
        return 2

    # Match the documented phrases case-insensitively; input remains data.
    phrases = (
        ("workflows", r"\bworkflows\b"),
        ("triggers", r"\btriggers\b"),
        ("capabilities", r"\bcapabilities\b"),
        ("DON consensus", r"\bDON consensus\b"),
        ("API fetch", r"\bfetch APIs\b|\bfetch data from API\b"),
        ("EVM read", r"\bread contracts\b|\bread from EVM blockchain\b"),
        ("computation", r"\bcomputation\b|\bmake any computation\b"),
        ("onchain write", r"\bwrite onchain\b|\bwrite result onchain\b"),
    )
    found = [name for name, pattern in phrases if re.search(pattern, text, re.IGNORECASE)]

    if not found:
        print("No recognized CRE overview terms found.")
        return 0

    print("CRE overview terms found:")
    for name in found:
        print(f"- {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
