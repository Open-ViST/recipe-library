# Validate CSV columns and detect duplicate rows with Python

Check required CSV columns and identify exact duplicate rows before an import.

Published recipe: [validate-csv-columns-detect-duplicate-rows-python](https://openvist.com/recipes/validate-csv-columns-detect-duplicate-rows-python/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.py`

from recipe import inspect_csv
result = inspect_csv("id,name\n1,Jose\n1,Jose\n", ["id", "name"])
print(result)

## Requirements

- Python 3.12; no external dependencies.
- Decoded CSV text using comma separators.
- Pass required column names as a list of strings.

## Steps

- Save the example code as recipe.py.
- Import inspect_csv and pass the CSV text and required column names.
- Inspect rows and duplicates in the returned dictionary.
- Handle ValueError and csv.Error before proceeding with an import.

## Checks

- Seven test methods passed in the pinned Python Docker image.
- Covered Unicode, BOM, duplicates, quoted commas and newlines.
- Covered header-only input, invalid structure and unclosed quotes.

## Limits

- Compares complete rows exactly, including whitespace and letter case.
- Does not validate data types or identifier uniqueness.
- Accepts decoded text, not a file path; encoding is the caller's responsibility.
- Record numbers count CSV records, not physical lines.
- Memory grows with distinct rows; use modest inputs.
- Header-only input is valid. Additional columns are allowed.

## Expected output

```text
{'rows': 2, 'duplicates': [{'record': 3, 'first_record': 2}]}
```

## Recorded validation scope

Seven unittest methods passed in an isolated Python 3.12 Docker container with networking disabled. Covers the listed fixtures; does not establish performance for large files or support for every CSV dialect.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/csv.html
- https://docs.python.org/3.12/library/io.html
