# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
import argparse
import json
import pathlib
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Check required top-level keys without printing configuration values."
    )
    parser.add_argument(
        "source",
        help="local JSON file path, or - to read JSON from standard input",
    )
    parser.add_argument(
        "--required",
        nargs="+",
        required=True,
        metavar="KEY",
        help="one or more required top-level keys",
    )
    args = parser.parse_args()

    try:
        if args.source == "-":
            text = sys.stdin.read()
        else:
            text = pathlib.Path(args.source).read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        print("error: could not read input", file=sys.stderr)
        return 2

    try:
        config = json.loads(text)
    except json.JSONDecodeError:
        print("error: invalid JSON", file=sys.stderr)
        return 2

    if not isinstance(config, dict):
        print("error: JSON root must be an object", file=sys.stderr)
        return 2

    missing = sorted(set(args.required) - config.keys())
    if missing:
        print("missing keys: " + ", ".join(missing))
        return 1

    print("all required keys are present")
    return 0


if __name__ == "__main__":
    sys.exit(main())