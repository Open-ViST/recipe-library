# Find conflicting values assigned to record IDs with Python

Identify IDs associated with more than one distinct text value in supplied records.

Published recipe: [audit-identifier-value-conflicts-python](https://openvist.com/recipes/audit-identifier-value-conflicts-python/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.py`

python3 recipe.py < input.json

## Requirements

- Save the code as recipe.py and run python3.12 recipe.py. Supply the JSON document through stdin, then signal EOF. No arguments, including a help option, are accepted.
- Uses only json, sys and math. Reads stdin only; does not open input paths, write files, execute external commands or access a network.
- Input must be a JSON array of objects with nonempty string fields id and value. Additional fields are ignored after parsing. There are no integer fields; numeric and boolean IDs or values are rejected.
- Strings are compared exactly without trimming, case folding or Unicode normalization. Conflicts and distinct values are sorted by Python string ordering. Identical repeated pairs do not create conflicts.
- Duplicate JSON object keys follow json's last-key-wins convention. Integer tokens are parsed as a null sentinel because no integer fields are supported, avoiding integer-conversion digit limits in ignored fields. Nonfinite constants and floating-point overflow are rejected anywhere in the document.
- An empty array produces {"conflicts":[]}; empty stdin is invalid JSON.
- Success exits 0 and writes exactly one JSON object followed by a newline, with no stderr. Invalid arguments, invalid input and stdin read failures exit 2 with no stdout and the generic diagnostic error: invalid input on stderr. Output strings use JSON Unicode escapes where needed.

## Steps

- Use Python 3.12. Save the code as recipe.py.
- Save the supplied JSON example as input.json, encoded as UTF-8 without a BOM.
- Run: python3 recipe.py < input.json
- Compare the output with the expected result; handle exit code 2 as invalid input.

## Checks

- The supplied example must match the documented JSON output.
- Error cases must exit 2 with no stdout. Review sensitive successful output before sharing it.

## Limits

- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8 and rejects a leading UTF-8 BOM.
- Accepts at most 100 records. Each id and value must contain 1–80 Python string characters, not bytes.
- The parsed document, grouped values and serialized output are held in memory. Additional fields still consume parsing memory. Python JSON parsing depth and available memory can limit acceptance.
- Stdin can block while waiting for EOF.
- Successful output includes selected IDs and values, which may be sensitive. Error diagnostics do not disclose input values.
- Output-write failures are outside the stated exit-code and diagnostic guarantee.

## Example input

```text
[{"id": "a", "value": "x"}, {"id": "a", "value": "y"}]
```

## Expected output

```text
{"conflicts": [{"id": "a", "values": ["x", "y"]}]}
```

## Recorded validation scope

Six independent CLI fixtures and 30 curated supplementary checks passed in the pinned offline Python 3.12 container. This does not establish exhaustive correctness, production performance or compatibility with an external provider.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/json.html
- https://docs.python.org/3.12/library/sys.html
