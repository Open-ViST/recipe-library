# Validate each nonempty JSONL line as a JSON object

Read a saved JSONL fixture or standard input, count valid object records, and report one-based line numbers for malformed JSON or lines that decode to a non-object.

Published recipe: [validate-jsonl-object-records](https://openvist.com/recipes/validate-jsonl-object-records/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `validate_jsonl.py`

Save as `validate_jsonl.py`, then run `python validate_jsonl.py records.jsonl`. To validate piped input, run `python validate_jsonl.py < records.jsonl`. The script performs no network calls and has no retry behavior.

## Requirements

- Intended runner: Python 3.12; no tested minimum version is claimed.
- Uses only the Python standard library modules `argparse`, `json`, `pathlib`, and `sys`.
- For file input, the selected path must exist and be readable as UTF-8; otherwise the tool reports an input error to stderr and exits with status 2.
- The JSON module documents `json.loads` for decoding JSON, and argparse documents parsing positional CLI arguments. The task validates local fixture data, not an external model or service.

## Steps

- Save the code as `validate_jsonl.py`.
- Create a UTF-8 JSONL fixture with one JSON object per nonempty line.
- Run `python validate_jsonl.py path/to/fixture.jsonl`, or omit the path to read stdin.
- Review the valid-object count and every reported one-based line number.
- Use the exit status: 0 means all nonempty lines were objects, 1 means record validation errors, and 2 means the input could not be read.

## Checks

- Run with a fixture containing two object lines and confirm the count is 2 and status is valid.
- Add a blank line and confirm it does not change the count or create an error.
- Add a valid JSON array or scalar and confirm its exact one-based line is reported as not an object.
- Add malformed JSON and confirm its exact line number is reported while later lines are still checked.
- Run with an empty file and confirm a count of 0 and valid status.
- Run with a nonexistent path and confirm an input error and exit status 2.
- Pipe a fixture through stdin and confirm it is validated without supplying a path.

## Limits

- Blank or whitespace-only lines are ignored and are not counted as records.
- Only JSON syntax and top-level object type are checked; fields, schemas, duplicate keys, and application-level meaning are not validated.
- The complete input is read into memory. Python's JSON documentation cautions that parsing untrusted data can consume considerable CPU and memory; use appropriately bounded local fixtures.
- JSON decoding errors are reported by line number and decoder message, not by column position.
- The script writes its report to stdout and file-read diagnostics to stderr; it does not alter input files.

## Example input

```text
{"id": 1}

[2]
not-json
{"id": 3}

```

## Expected output

```text
valid object records: 2
line 3: expected a JSON object
line 4: malformed JSON (Expecting value)
```

## Recorded validation scope

Executed 5 synthetic local fixture cases in isolated CPython 3.12.15 on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/json.html
- https://docs.python.org/3.12/library/argparse.html
