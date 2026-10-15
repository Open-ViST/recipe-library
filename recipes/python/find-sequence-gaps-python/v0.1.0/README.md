# Find compressed gaps in increasing event offsets with Python

Report missing ranges between supplied integer event offsets without expanding every missing number.

Published recipe: [find-sequence-gaps-python](https://openvist.com/recipes/find-sequence-gaps-python/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.py`

python3 recipe.py < input.json

## Requirements

- Save the code as recipe.py and run python3.12 recipe.py with a JSON array supplied through stdin. No CLI arguments, including a help option, are accepted.
- Uses only json, sys and math. It does not open input paths, write files, execute external commands or contact a network.
- Input must be strict UTF-8 JSON without a leading UTF-8 BOM. Malformed JSON, NaN, Infinity, -Infinity and floating-point overflow are rejected during parsing.
- The array must contain at most 1000 integers from 0 through 1000000000. Booleans and floating-point numbers are rejected, including floats that represent whole numbers. Values must be strictly increasing.
- Each gap has inclusive start and end boundaries. Gaps are emitted in ascending order, and missing_count counts only missing offsets between supplied values. Nothing is inferred before the first or after the last offset. Empty and singleton arrays produce no gaps.
- Successful processing exits 0, writes exactly one JSON object followed by a newline to stdout, and writes nothing to stderr. Invalid input, arguments or stdin read failures exit 2 with no stdout and the generic lowercase diagnostic error: invalid input on stderr.

## Steps

- Use Python 3.12. Save the code as recipe.py.
- Save the supplied JSON example as input.json, encoded as UTF-8 without a BOM.
- Run: python3 recipe.py < input.json
- Compare the output with the expected result; handle exit code 2 as invalid input.

## Checks

- The supplied example must match the documented JSON output.
- Error cases must exit 2 with no stdout. Review sensitive successful output before sharing it.

## Limits

- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Stdin can block waiting for EOF; no timeout is implemented.
- The raw input, decoded text and parsed input are held in memory. Valid-input processing takes linear time in the number of supplied offsets and stores at most 999 compressed gaps, without expanding individual missing offsets.
- Python's JSON parser nesting limits and integer-conversion limits may also reject input.
- Successful output can reveal sensitive offset ranges and counts. Diagnostics do not disclose input values.
- Output-write failures, including failures writing or flushing stdout, are outside the exit-code and diagnostic guarantees.

## Example input

```text
[1, 4, 5]
```

## Expected output

```text
{"gaps": [{"start": 2, "end": 3}], "missing_count": 2}
```

## Recorded validation scope

Six independent CLI fixtures and 10 curated supplementary checks passed in the pinned offline Python 3.12 container. This does not establish exhaustive correctness, production performance or compatibility with an external provider.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/json.html
- https://docs.python.org/3.12/library/sys.html
