# Convert JSON Lines to a predictable CSV

Export a small JSONL file with explicit columns, correct quoting and checks for invalid records.

Published recipe: [convert-jsonl-to-csv](https://openvist.com/recipes/convert-jsonl-to-csv/)

**Language:** python · **Version:** 1.0.0 · **License:** MIT

## Usage

Code file: `recipe.py`

See requirements below.

## Requirements

- Python 3.10 or later; standard library only.
- UTF-8 JSONL with one JSON object per nonblank line.
- Choose 1–32 distinct column names; input is limited to 8 MiB and 10,000 records.

## Steps

- Inspect the input and choose the desired column order.
- Run: python jsonl_csv.py records.jsonl --columns name,url,category > records.csv
- Keep the output path different from the input path: shell redirection truncates an existing output before the script starts.
- Open the CSV and verify its header, row count and expected cells.

## Checks

- Test commas, newlines, Unicode, missing fields and nested JSON.
- Malformed JSON, duplicate keys and non-object records must fail without partial CSV.
- Non-finite or overflowing numbers, excessive records and large input must return a nonzero exit status.

## Limits

- Only selected top-level fields are exported. Nested objects and lists become JSON text; the conversion is not a lossless JSON backup.
- Strings beginning with formula markers after whitespace get an apostrophe. Actual negative numbers remain numeric. This can alter display and must be checked in the target spreadsheet.
- The whole bounded input is validated before output. An output-stream failure can still interrupt a write.

## Recorded validation scope

Executed locally with deterministic fixtures and CLI checks on Python 3.12.14. The three scripts pass 22 tests covering valid output, invalid input and size limits. No network or provider call was made.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3/library/csv.html
- https://docs.python.org/3/library/json.html
