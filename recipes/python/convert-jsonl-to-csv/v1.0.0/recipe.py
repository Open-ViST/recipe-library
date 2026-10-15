# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
"""Convert a bounded UTF-8 JSON Lines file to selected CSV columns."""
import argparse
import csv
import json
import math
import re
import sys

MAX_BYTES = 8 * 1024 * 1024
MAX_RECORDS = 10000


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"non-finite JSON number: {value}")


def finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("JSON number exceeds the finite float range")
    return number


def cell(value):
    if value is None:
        return ""
    if isinstance(value, (dict, list, bool)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def convert(source, target, columns):
    if not 1 <= len(columns) <= 32 or len(set(columns)) != len(columns):
        raise ValueError("choose 1–32 distinct columns")
    if any(not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_. -]{0,63}", name) for name in columns):
        raise ValueError("invalid column name")
    raw = source.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("input exceeds 8 MiB")
    rows = []
    for line_number, line in enumerate(raw.decode("utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line, object_pairs_hook=unique_object,
                             parse_constant=reject_constant, parse_float=finite_float)
        except (ValueError, RecursionError) as error:
            raise ValueError(f"invalid JSON on line {line_number}: {error}") from error
        if not isinstance(row, dict):
            raise ValueError(f"line {line_number} must contain a JSON object")
        rows.append(row)
        if len(rows) > MAX_RECORDS:
            raise ValueError("input exceeds 10,000 records")
    # Validate the whole input before emitting a header or any partial CSV.
    writer = csv.DictWriter(target, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({name: cell(row.get(name)) for name in columns})
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="UTF-8 JSONL file")
    parser.add_argument("--columns", required=True, help="comma-separated column names")
    args = parser.parse_args()
    try:
        with open(args.input, "rb") as source:
            convert(source, sys.stdout, [name.strip() for name in args.columns.split(",")])
    except (OSError, ValueError, UnicodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
