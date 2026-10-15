# Audit parent references in JSON task records with Python

Find roots and undeclared parent identifiers in a small task-record collection.

Published recipe: [audit-parent-references-python](https://openvist.com/recipes/audit-parent-references-python/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.py`

python3 recipe.py < input.json

## Requirements

- Save the code as recipe.py and supply JSON through stdin to python3.12 recipe.py. No arguments are accepted, including --help.
- Uses only json, sys and math. Reads stdin only; does not open paths, write files, run external commands or access a network.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Decoding is strict UTF-8; a leading UTF-8 BOM, malformed JSON, nonstandard numeric constants and floating-point overflow are rejected before record processing.
- Requires an array of at most 100 objects with unique IDs. Every object must contain id and parent. IDs and non-null parents must be strings containing 1 through 80 characters.
- Null parents identify roots. Non-null parents absent from the complete ID set identify dangling references. Roots and dangling records are sorted by Python string order, with dangling records sorted by child ID. An empty array produces empty lists.
- Successful processing exits 0 and writes one JSON object followed by a newline, with no stderr. Invalid arguments, invalid input and stdin read failures exit 2, produce no stdout and write only error: invalid input to stderr.

## Steps

- Use Python 3.12. Save the code as recipe.py.
- Save the supplied JSON example as input.json, encoded as UTF-8 without a BOM.
- Run: python3 recipe.py < input.json
- Compare the output with the expected result; handle exit code 2 as invalid input.

## Checks

- The supplied example must match the documented JSON output.
- Error cases must exit 2 with no stdout. Review sensitive successful output before sharing it.

## Limits

- String comparisons are exact and case-sensitive, without Unicode normalization. Lengths count Python string characters, not UTF-8 bytes. Escaped lone surrogates accepted by Python's JSON parser remain escaped in output.
- Additional fields are ignored after parsing. Repeated JSON object member names use Python's default last-value-wins convention. There are no integer-valued schema fields; booleans cannot satisfy either identifier field.
- All input and parsed records are held in memory. Parsing can consume substantially more memory than the byte limit, and interpreter recursion or resource failures are reported through the generic error path.
- Stdin can block while waiting for data or EOF. There is no timeout.
- Self-references are declared references and are not dangling. Cycles are not detected, and the output makes no claim of acyclicity.
- Successful output contains task identifiers and parent identifiers and may be sensitive.
- Output-write failures, including stdout write or flush failures, are outside the exit-status and diagnostic guarantees.

## Example input

```text
[{"id": "a", "parent": null}, {"id": "b", "parent": "a"}, {"id": "c", "parent": "missing"}]
```

## Expected output

```text
{"roots": ["a"], "dangling": [{"id": "c", "parent": "missing"}]}
```

## Recorded validation scope

Six independent CLI fixtures and 10 curated supplementary checks passed in the pinned offline Python 3.12 container. This does not establish exhaustive correctness, production performance or compatibility with an external provider.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/json.html
- https://docs.python.org/3.12/library/sys.html
