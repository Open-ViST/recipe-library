# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Validate a local XML workflow root and call attributes."
    )
    parser.add_argument("file", help="XML path, or - to read standard input")
    parser.add_argument("--root-tag", required=True, help="Exact required root tag")
    parser.add_argument("--call-tag", required=True, help="Exact tag identifying calls")
    args = parser.parse_args()

    if not args.root_tag or not args.call_tag:
        parser.error("--root-tag and --call-tag must not be empty")

    try:
        if args.file == "-":
            source = sys.stdin.read()
        else:
            source = Path(args.file).read_text(encoding="utf-8")
        root = ET.fromstring(source)
    except FileNotFoundError:
        print("ERROR: input file not found", file=sys.stderr)
        return 2
    except UnicodeDecodeError:
        print("ERROR: input is not valid UTF-8", file=sys.stderr)
        return 2
    except ET.ParseError as exc:
        print(f"ERROR: malformed XML: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERROR: cannot read input: {exc}", file=sys.stderr)
        return 2

    problems = []
    if root.tag != args.root_tag:
        problems.append(f"root tag is {root.tag!r}; expected {args.root_tag!r}")

    calls = list(root.iter(args.call_tag))
    for index, call in enumerate(calls, start=1):
        for attribute in ("name", "arguments"):
            if not call.get(attribute, "").strip():
                problems.append(f"{args.call_tag} #{index} has missing or empty {attribute}")

    if problems:
        for problem in problems:
            print(f"INVALID: {problem}")
        return 1

    print(f"OK: root={root.tag}; {len(calls)} call element(s) validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())