# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
import argparse
import json
import sys
import xml.etree.ElementTree as ET


def reject_constant(value):
    raise ValueError("non-standard JSON constant: " + value)


def main():
    parser = argparse.ArgumentParser(
        description="Validate JSON in arguments attributes of local XML tool-call elements."
    )
    parser.add_argument("xml_file", help="XML fixture path, or - to read standard input")
    parser.add_argument(
        "--tag",
        default="tool_call",
        help="exact element tag to inspect (default: tool_call)",
    )
    args = parser.parse_args()

    if not args.tag:
        parser.error("--tag must not be empty")

    try:
        if args.xml_file == "-":
            source = sys.stdin.read()
            root = ET.fromstring(source)
        else:
            root = ET.parse(args.xml_file).getroot()
    except FileNotFoundError:
        print("error: input file not found", file=sys.stderr)
        return 2
    except (OSError, ET.ParseError) as exc:
        print(f"error: cannot read or parse XML: {exc}", file=sys.stderr)
        return 2

    inspected = 0
    invalid = []
    for position, element in enumerate(root.iter(args.tag), start=1):
        inspected += 1
        raw = element.get("arguments")
        try:
            if raw is None:
                raise ValueError("missing arguments attribute")
            json.loads(raw, parse_constant=reject_constant)
        except (json.JSONDecodeError, ValueError):
            invalid.append(position)

    if invalid:
        print(f"invalid: {len(invalid)} of {inspected} matching elements")
        for position in invalid:
            print(f"element {position}: missing or invalid JSON arguments")
    else:
        print(f"valid: {inspected} matching elements; all arguments are JSON")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())