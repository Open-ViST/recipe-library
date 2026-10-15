# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
import argparse
import json
import pathlib
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Validate nonempty JSONL lines as JSON objects."
    )
    parser.add_argument(
        "path", nargs="?", help="JSONL file to read; omit to read standard input"
    )
    args = parser.parse_args()

    try:
        if args.path is None:
            text = sys.stdin.read()
        else:
            text = pathlib.Path(args.path).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2

    record_count = 0
    errors = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_number}: malformed JSON ({exc.msg})")
            continue
        if not isinstance(value, dict):
            errors.append(f"line {line_number}: expected a JSON object")
            continue
        record_count += 1

    print(f"valid object records: {record_count}")
    if errors:
        for error in errors:
            print(error)
        return 1
    print("status: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())