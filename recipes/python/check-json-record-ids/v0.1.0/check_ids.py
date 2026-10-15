# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Report missing, empty, and duplicate string IDs in a JSON array."
    )
    parser.add_argument("file", help="path to a saved JSON file")
    parser.add_argument("--field", required=True, help="object field containing the ID")
    args = parser.parse_args()

    try:
        text = Path(args.file).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read input file: {exc}", file=sys.stderr)
        return 2

    try:
        records = json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON at line {exc.lineno}, column {exc.colno}", file=sys.stderr)
        return 2

    if not isinstance(records, list):
        print("error: top-level JSON value must be an array", file=sys.stderr)
        return 2

    missing = []
    empty = []
    non_string = []
    positions_by_id = {}

    for position, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            print(f"error: record {position} is not an object", file=sys.stderr)
            return 2
        if args.field not in record:
            missing.append(position)
            continue
        value = record[args.field]
        if not isinstance(value, str):
            non_string.append(position)
            continue
        if not value.strip():
            empty.append(position)
            continue
        positions_by_id.setdefault(value, []).append(position)

    duplicates = [
        (value, positions)
        for value, positions in positions_by_id.items()
        if len(positions) > 1
    ]

    print(f"records: {len(records)}")
    print(f"missing {args.field}: {len(missing)} at {missing}")
    print(f"empty {args.field}: {len(empty)} at {empty}")
    print(f"non-string {args.field}: {len(non_string)} at {non_string}")
    print(f"duplicate IDs: {len(duplicates)}")
    for value, positions in duplicates:
        print(f"  {value!r}: records {positions}")
    return 0


if __name__ == "__main__":
    sys.exit(main())