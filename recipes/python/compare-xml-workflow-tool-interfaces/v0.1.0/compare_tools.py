# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def signatures(path):
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as exc:
        raise ValueError(f"cannot read valid XML from {path}: {exc}") from exc

    found = set()
    for elem in root.iter():
        # A tool element is identified by the exact, case-sensitive local tag name.
        local_tag = elem.tag.rsplit("}", 1)[-1] if isinstance(elem.tag, str) else ""
        if local_tag == "tool":
            found.add((elem.tag, tuple(sorted(elem.attrib.items()))))
    return found


def main():
    parser = argparse.ArgumentParser(
        description="Compare exact tool-element signatures in two saved XML workflows."
    )
    parser.add_argument("before", help="path to the earlier XML workflow")
    parser.add_argument("after", help="path to the later XML workflow")
    args = parser.parse_args()

    try:
        before = signatures(Path(args.before))
        after = signatures(Path(args.after))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    def display(signature):
        tag, attrs = signature
        return {"tag": tag, "attributes": dict(attrs)}

    result = {
        "added": [display(item) for item in sorted(after - before)],
        "removed": [display(item) for item in sorted(before - after)],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())