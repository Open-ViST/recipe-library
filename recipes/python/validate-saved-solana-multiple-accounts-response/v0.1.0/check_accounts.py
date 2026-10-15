# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
import argparse
import json
import pathlib
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Check owner and lamports in a saved getMultipleAccounts response."
    )
    parser.add_argument("file", help="Saved JSON response file, or - to read stdin")
    args = parser.parse_args()

    try:
        if args.file == "-":
            text = sys.stdin.read()
        else:
            text = pathlib.Path(args.file).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read input: {exc}", file=sys.stderr)
        return 1

    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON: {exc}", file=sys.stderr)
        return 1

    if not isinstance(document, dict):
        print("error: top-level JSON value must be an object", file=sys.stderr)
        return 1
    if "error" in document:
        print("error: response contains an RPC error", file=sys.stderr)
        return 1

    result = document.get("result")
    if not isinstance(result, dict):
        print("error: result must be an object", file=sys.stderr)
        return 1
    values = result.get("value")
    if not isinstance(values, list):
        print("error: result.value must be an array", file=sys.stderr)
        return 1

    rows = []
    invalid = False
    for index, account in enumerate(values):
        if account is None:
            rows.append({"index": index, "status": "null"})
            continue
        if not isinstance(account, dict):
            rows.append({"index": index, "status": "invalid", "reason": "account must be an object or null"})
            invalid = True
            continue

        owner = account.get("owner")
        lamports = account.get("lamports")
        problems = []
        if not isinstance(owner, str) or not owner:
            problems.append("owner must be a non-empty string")
        if isinstance(lamports, bool) or not isinstance(lamports, int) or lamports < 0:
            problems.append("lamports must be a non-negative integer")

        if problems:
            rows.append({"index": index, "status": "invalid", "reason": "; ".join(problems)})
            invalid = True
        else:
            rows.append({"index": index, "status": "valid", "owner": owner, "lamports": lamports})

    print(json.dumps(rows, indent=2))
    return 1 if invalid else 0


if __name__ == "__main__":
    sys.exit(main())