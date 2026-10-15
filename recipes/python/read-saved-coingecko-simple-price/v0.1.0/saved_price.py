# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
import argparse
import json
import math
import pathlib
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Read one price from a saved CoinGecko simple-price JSON response."
    )
    parser.add_argument("file", help="path to a saved JSON response, or - for stdin")
    parser.add_argument("asset_id", help="explicit CoinGecko asset ID, such as bitcoin")
    parser.add_argument("currency", help="quote currency key, such as usd")
    args = parser.parse_args()

    if not args.asset_id or not args.currency:
        parser.error("asset_id and currency must not be empty")

    try:
        if args.file == "-":
            text = sys.stdin.read()
        else:
            text = pathlib.Path(args.file).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read input: {exc}", file=sys.stderr)
        return 2

    try:
        response = json.loads(text, parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"invalid non-finite JSON constant: {value}")
        ))
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"error: invalid JSON: {exc}", file=sys.stderr)
        return 2

    if not isinstance(response, dict):
        print("error: expected a top-level JSON object", file=sys.stderr)
        return 2
    asset = response.get(args.asset_id)
    if not isinstance(asset, dict):
        print(f"error: asset ID {args.asset_id!r} is absent or is not an object", file=sys.stderr)
        return 2
    if args.currency not in asset:
        print(f"error: currency {args.currency!r} is absent for {args.asset_id!r}", file=sys.stderr)
        return 2

    price = asset[args.currency]
    if isinstance(price, bool) or not isinstance(price, (int, float)):
        print("error: price must be a non-null JSON number", file=sys.stderr)
        return 2
    if not math.isfinite(price):
        print("error: price must be finite", file=sys.stderr)
        return 2

    print(f"Saved observation: {args.asset_id}/{args.currency} = {price}")
    print("This is a saved observation, not a current quote.")
    return 0


if __name__ == "__main__":
    sys.exit(main())