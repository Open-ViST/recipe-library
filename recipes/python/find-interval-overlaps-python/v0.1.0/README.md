# Find overlaps between bounded integer intervals with Python

Report overlapping half-open intervals using original one-based positions.

Published recipe: [find-interval-overlaps-python](https://openvist.com/recipes/find-interval-overlaps-python/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.py`

python3 recipe.py < input.json

## Requirements

- Save the code as recipe.py and run python3.12 recipe.py with JSON supplied on stdin. No arguments, including a help option, are accepted. The CLI imports only json, sys and math.
- Input must be an array of at most 20 objects. Each object must contain start and end as integers, excluding booleans, from 0 through 1000000000 inclusive, with start < end. Additional fields are ignored after JSON parsing.
- Intervals are half-open: [start, end). Touching endpoints do not overlap. Positions are the original one-based array positions, and results are ordered by first and then second. Offsets are unitless, not dates or timezone values.
- Success exits 0 and writes exactly one JSON object to stdout without stderr. An empty input array returns {"overlaps":[]}. Invalid input, arguments or stdin read failures exit 2 with no stdout and the generic lowercase stderr diagnostic error: invalid input.
- Input is decoded as strict UTF-8. A leading UTF-8 BOM, malformed JSON, NaN, Infinity, -Infinity and floating-point overflow are rejected. Python's JSON convention for duplicate object keys applies: the last occurrence is used.
- The CLI reads stdin only; it does not open input paths, write files, execute external commands or contact a network.

## Steps

- Use Python 3.12. Save the code as recipe.py.
- Save the supplied JSON example as input.json, encoded as UTF-8 without a BOM.
- Run: python3 recipe.py < input.json
- Compare the output with the expected result; handle exit code 2 as invalid input.

## Checks

- The supplied example must match the documented JSON output.
- Error cases must exit 2 with no stdout. Review sensitive successful output before sharing it.

## Limits

- Reads at most 65537 bytes and rejects input exceeding 65536 bytes, including whitespace. Stdin can block while waiting for EOF.
- The input bytes, decoded text, parsed JSON and results are held in memory. The byte limit bounds source input size, not exact memory consumption; parsed structures add overhead.
- At most 190 interval pairs are checked and at most 190 overlap records are returned.
- Successful output reveals original positions and overlapping ranges and may therefore be sensitive.
- Output-write failures, including stdout flush failures, are outside the stated exit-code and diagnostic guarantee.
- The interpreter's integer-conversion and JSON nesting limits can also cause input rejection. No provider integration, production suitability or uniqueness is claimed.

## Example input

```text
[{"start": 0, "end": 5}, {"start": 3, "end": 7}]
```

## Expected output

```text
{"overlaps": [{"first": 1, "second": 2, "start": 3, "end": 5}]}
```

## Recorded validation scope

Six independent CLI fixtures and 10 curated supplementary checks passed in the pinned offline Python 3.12 container. This does not establish exhaustive correctness, production performance or compatibility with an external provider.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/json.html
- https://docs.python.org/3.12/library/sys.html
