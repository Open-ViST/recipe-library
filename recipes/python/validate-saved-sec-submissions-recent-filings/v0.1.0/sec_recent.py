# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
import argparse
import json
import sys
from pathlib import Path

FIELDS = ("form", "filingDate", "accessionNumber", "primaryDocument")


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def main():
    parser = argparse.ArgumentParser(
        description="Validate and summarize recent filings in a saved SEC submissions JSON file."
    )
    parser.add_argument("file", help="saved JSON path, or - to read JSON from stdin")
    args = parser.parse_args()

    try:
        if args.file == "-":
            text = sys.stdin.read()
        else:
            text = Path(args.file).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        fail(f"cannot read input: {exc}")

    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON at line {exc.lineno}, column {exc.colno}")

    if not isinstance(document, dict):
        fail("top-level JSON value must be an object")
    filings = document.get("filings")
    if not isinstance(filings, dict):
        fail("filings must be an object")
    recent = filings.get("recent")
    if not isinstance(recent, dict):
        fail("filings.recent must be an object")

    arrays = {}
    for field in FIELDS:
        value = recent.get(field)
        if not isinstance(value, list):
            fail(f"filings.recent.{field} must be an array")
        arrays[field] = value

    lengths = {field: len(values) for field, values in arrays.items()}
    if len(set(lengths.values())) != 1:
        detail = ", ".join(f"{field}={lengths[field]}" for field in FIELDS)
        fail(f"recent filing arrays have unequal lengths ({detail})")

    count = lengths["form"]
    if count == 0:
        print("No recent filing records.")
        return

    print(f"Recent filing records: {count}")
    for index in range(count):
        values = [arrays[field][index] for field in FIELDS]
        if not all(isinstance(value, str) for value in values):
            fail(f"record {index + 1} contains a non-string field")
        form, filing_date, accession, primary_document = values
        print(f"{index + 1}. {form} | {filing_date} | {accession} | {primary_document}")


if __name__ == "__main__":
    main()
