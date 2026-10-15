# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
import argparse
import pathlib
import re
import sys


def main():
    parser = argparse.ArgumentParser(
        description="List RPC method names from a saved Bitcoin developer reference text file."
    )
    parser.add_argument("reference", help="Path to a UTF-8 text copy of the reference")
    args = parser.parse_args()

    try:
        text = pathlib.Path(args.reference).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"error: cannot read reference file: {exc}", file=sys.stderr)
        return 2

    if not text.strip():
        print("error: reference file is empty", file=sys.stderr)
        return 2

    start_marker = "RPC API Reference"
    end_marker = "Network Status"
    start = text.find(start_marker)
    if start < 0:
        print(f"error: missing section marker {start_marker!r}", file=sys.stderr)
        return 2
    end = text.find(end_marker, start + len(start_marker))
    if end < 0:
        print(f"error: missing section boundary {end_marker!r}", file=sys.stderr)
        return 2

    section = text[start + len(start_marker):end]
    # The reference presents method names directly before “Argument” or “Result”.
    names = re.findall(r"(?<![A-Za-z0-9_])([a-z][a-z0-9]+)(?=\s+Argument\s+#|\s+Result\b)", section)
    distinct_names = sorted(set(names))
    if not distinct_names:
        print("error: no RPC method names found in the selected section", file=sys.stderr)
        return 2

    for name in distinct_names:
        print(name)
    return 0


if __name__ == "__main__":
    sys.exit(main())