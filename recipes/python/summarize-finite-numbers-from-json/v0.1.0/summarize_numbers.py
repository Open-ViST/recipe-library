# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
import argparse
import json
import math
import pathlib
import sys


def reject_nonfinite_constant(value):
    raise ValueError(f"non-finite JSON number is not allowed: {value}")


def main():
    parser = argparse.ArgumentParser(
        description="Summarize a JSON array of finite numbers from a file or stdin."
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="JSON file to read; omit this argument to read stdin",
    )
    args = parser.parse_args()

    try:
        if args.file:
            text = pathlib.Path(args.file).read_text(encoding="utf-8")
        else:
            text = sys.stdin.read()

        data = json.loads(text, parse_constant=reject_nonfinite_constant)
        if not isinstance(data, list):
            raise ValueError("top-level JSON value must be an array")

        values = []
        for index, value in enumerate(data, start=1):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"item {index} must be a number, not a boolean or other value")
            if not math.isfinite(value):
                raise ValueError(f"item {index} must be finite")
            values.append(value)

        if not values:
            print("count: 0")
            print("min: n/a")
            print("max: n/a")
            print("mean: n/a")
            return 0

        mean = sum(values) / len(values)
        if not math.isfinite(mean):
            raise ValueError("mean is not finite; numeric values may be too large")

        print(f"count: {len(values)}")
        print(f"min: {min(values)}")
        print(f"max: {max(values)}")
        print(f"mean: {mean}")
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, OverflowError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())