# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
import argparse
import json
import pathlib
import sys
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser(
        description="Inspect matching elements in a local XML file without running it."
    )
    parser.add_argument("xml_file", help="local XML file to inspect")
    parser.add_argument("tag", help="exact element tag name to select")
    args = parser.parse_args()

    if not args.tag.strip():
        parser.error("tag must not be blank")

    try:
        text = pathlib.Path(args.xml_file).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2

    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        print(f"XML parse error: {exc}", file=sys.stderr)
        return 2

    matches = [
        {"tag": element.tag, "attributes": dict(element.attrib)}
        for element in root.iter(args.tag)
    ]
    print(json.dumps(matches, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())