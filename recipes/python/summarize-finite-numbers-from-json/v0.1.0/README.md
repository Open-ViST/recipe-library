# Summarize finite numbers in a local JSON array

Read a local JSON array of finite numbers, reject booleans and other invalid values, and print its count, minimum, maximum, and arithmetic mean.

Published recipe: [summarize-finite-numbers-from-json](https://openvist.com/recipes/summarize-finite-numbers-from-json/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `summarize_numbers.py`

Save as `summarize_numbers.py`, then run `python3.12 summarize_numbers.py observations.json` or pipe input with `printf '[2, 4, 6]\n' | python3.12 summarize_numbers.py`. The intended runner is Python 3.12; no other minimum-version claim is made. There are no network calls, retries, or timeout requirement.

## Requirements

- Python 3.12 is the intended runner; the cited Python 3.12 documentation describes the standard-library `json` module and finite-value concerns for statistical data.
- Provide a UTF-8 JSON file path or pipe one JSON document to stdin. The top-level value must be an array.
- Every array item must be a finite integer or float. Booleans, strings, null, arrays, objects, NaN, and infinities are rejected.
- The summary is only about the saved values supplied to the program; it is not a live-service check or financial advice.

## Steps

- Save the code as `summarize_numbers.py`.
- Create a synthetic fixture containing `[2, 4, 6]` and run `python3.12 summarize_numbers.py observations.json`.
- Confirm the displayed count, minimum, maximum, and mean match the fixture.
- Try an empty array, malformed JSON, a non-array top-level value, a boolean or string element, and a non-finite number; confirm empty input is explicit and invalid input exits with an error.
- Run with a nonexistent file path and confirm the missing-file error is written to stderr.

## Checks

- Run the normal synthetic example and verify all four output lines exactly.
- Run with `[]` and verify `count: 0` and `n/a` for min, max, and mean.
- Run malformed JSON and confirm a clear stderr message and nonzero exit status.
- Run `[true]`, `["3"]`, `[null]`, and `[NaN]`; confirm each is rejected rather than coerced.
- Run a top-level object such as `{}` and confirm it is rejected as not an array.
- Use a nonexistent fixture path and confirm the missing-file condition is reported.

## Limits

- This reports descriptive statistics for only the values supplied; it does not establish whether observations are representative or current.
- The mean may be sensitive to outliers. No filtering, coercion, or missing-value imputation is performed.
- Parsing untrusted JSON can consume significant CPU or memory; use appropriately small local input files.
- A finite input set can still produce an unrepresentable floating-point mean for extreme values; that case is reported as an error.

## Example input

```text
[2, 4, 6]
```

## Expected output

```text
count: 3
min: 2
max: 6
mean: 4.0
```

## Recorded validation scope

Executed 6 synthetic local fixture cases in isolated CPython 3.12.15 on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/statistics.html
- https://docs.python.org/3.12/library/json.html
