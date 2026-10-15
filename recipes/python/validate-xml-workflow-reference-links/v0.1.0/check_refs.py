# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def check_references(root):
    declared = {element.get("id") for element in root.iter() if element.get("id")}
    missing = []
    for element in root.iter():
        ref = element.get("ref")
        if ref and ref not in declared:
            missing.append((element.tag, ref))
    return missing


def main():
    parser = argparse.ArgumentParser(
        description="Report XML elements whose ref attribute has no matching id."
    )
    parser.add_argument("file", help="local XML fixture path, or - to read stdin")
    args = parser.parse_args()

    try:
        if args.file == "-":
            xml_text = sys.stdin.read()
        else:
            xml_text = Path(args.file).read_text(encoding="utf-8")
        root = ET.fromstring(xml_text)
    except FileNotFoundError:
        print("error: input file not found", file=sys.stderr)
        return 2
    except (OSError, UnicodeError, ET.ParseError) as exc:
        print(f"error: cannot read or parse XML: {exc}", file=sys.stderr)
        return 2

    missing = check_references(root)
    if not missing:
        print("No unresolved ref attributes.")
    else:
        for tag, ref in missing:
            print(f"unresolved ref={ref!r} on <{tag}>")
    return 0


if __name__ == "__main__":
    sys.exit(main())