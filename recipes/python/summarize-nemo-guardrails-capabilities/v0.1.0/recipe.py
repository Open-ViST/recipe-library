# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
from pathlib import Path
import sys

SOURCE = Path("nemo_guardrails_overview.txt")
CAPABILITIES = (
    "LLM self-checking",
    "NVIDIA safety models",
    "Community models",
    "Third-party APIs",
    "Self-check jailbreak detection",
    "Heuristic detection",
    "NVIDIA NemoGuard",
    "Third-party integrations",
)


def main() -> int:
    try:
        text = SOURCE.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Input file not found: {SOURCE}", file=sys.stderr)
        return 1
    except (OSError, UnicodeError) as exc:
        print(f"Could not read UTF-8 input: {exc}", file=sys.stderr)
        return 1

    found = [name for name in CAPABILITIES if name in text]
    if not found:
        print("No listed safety capabilities found; check that this is the expected overview text.", file=sys.stderr)
        return 2

    print("Safety capabilities named in the supplied overview:")
    for name in found:
        print(f"- {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())