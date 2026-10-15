# Check a JSON array for missing, empty, or duplicate string IDs

Read a saved JSON array of objects and report one-based record positions with missing, empty, or duplicate string IDs in a CLI-selected field, without changing the input.

Published recipe: [check-json-record-ids](https://openvist.com/recipes/check-json-record-ids/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `check_ids.py`

Save as `check_ids.py`, then run: `python check_ids.py records.json --field id`. The recipe targets Python 3.12 and uses only its standard library; it does not require network access, credentials, or an external service. The code is a proposed example and should be independently checked before publication.

## Requirements

- Python 3.12 is the intended runner; the supplied official documentation is for Python 3.12. The sources do not establish a minimum compatible version.
- A readable local UTF-8 JSON file whose top-level value is an array; each record must be an object for the check to complete.
- A CLI-selected `--field` name. String IDs containing only whitespace are classified as empty; non-string values are reported separately.
- Only Python standard-library modules are used. No service, credential, network access, or installation is involved.

## Steps

- Save the code as `check_ids.py` and prepare a small local JSON fixture.
- Run it with a file path and required `--field` argument.
- For each object, distinguish an absent field, a non-string value, a whitespace-only string, and a nonempty string ID.
- Collect positions for each nonempty string and report IDs occurring at multiple one-based positions.
- Print overall and category counts without editing, deleting, or rewriting records.
- Use the error messages and checks below to diagnose invalid input or filesystem issues.

## Checks

- Run the synthetic fixture above and confirm the one-based positions and counts match the expected output.
- Run with an empty JSON array (`[]`) and confirm all issue counts are zero and the record count is zero.
- Try a malformed JSON file and confirm it reports a JSON line and column on stderr rather than a traceback.
- Try a JSON object as the top-level value and a top-level array containing a non-object; confirm each is rejected with a clear error.
- Try a path that does not exist and confirm a read error is reported on stderr.
- Try IDs that are `null`, numeric, empty, and whitespace-only; confirm non-strings and empty strings are counted separately.

## Limits

- The file is read wholly into memory; do not use it for untrusted, extremely large JSON input without adding suitable size limits.
- Duplicate comparison is exact and case-sensitive; values are not normalized or coerced.
- The code rejects a non-array top level and stops at the first non-object record rather than producing partial results.
- Read errors and malformed JSON exit with status 2; they are reported on stderr. There are no retries or network timeouts because the task has no network calls.

## Example input

```text
[
  {"id": "a1"},
  {"id": ""},
  {},
  {"id": "a1"},
  {"id": 7}
]
```

## Expected output

```text
records: 5
missing id: 1 at [3]
empty id: 1 at [2]
non-string id: 1 at [5]
duplicate IDs: 1
  'a1': records [1, 4]
```

## Recorded validation scope

Executed 6 synthetic local fixture cases in isolated CPython 3.12.15 on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/collections.html
- https://docs.python.org/3.12/library/json.html
