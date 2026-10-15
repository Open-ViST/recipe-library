# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
def effective_quote_reserves(vault_amount: int, virtual_reserves: int) -> int:
    if isinstance(vault_amount, bool) or not isinstance(vault_amount, int):
        raise TypeError("vault_amount must be an integer")
    if isinstance(virtual_reserves, bool) or not isinstance(virtual_reserves, int):
        raise TypeError("virtual_reserves must be an integer")
    if vault_amount < 0:
        raise ValueError("vault_amount must be non-negative")

    effective = vault_amount + virtual_reserves
    if effective < 0:
        raise ValueError("effective reserves cannot be negative")
    return effective


if __name__ == "__main__":
    import argparse
    import sys
    parser = argparse.ArgumentParser(description="Calculate effective quote reserves from local integer values.")
    parser.add_argument("vault_amount", type=int)
    parser.add_argument("virtual_reserves", type=int)
    args = parser.parse_args()
    try:
        result = effective_quote_reserves(args.vault_amount, args.virtual_reserves)
    except (TypeError, ValueError) as exc:
        print(f"Invalid pool values: {exc}", file=sys.stderr)
        raise SystemExit(2)
    print(f"Effective quote reserves: {result}")
