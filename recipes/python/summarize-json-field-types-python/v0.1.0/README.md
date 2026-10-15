# Summarize field presence and value types in JSON records with Python

Inspect a small JSON array of objects and report field coverage and top-level value type counts without printing the values.

Published recipe: [summarize-json-field-types-python](https://openvist.com/recipes/summarize-json-field-types-python/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `summarize.py`

python3 summarize.py < records.json

## Requirements

- Run with Python 3.12 as python3.12 summarize.py, supplying JSON through standard input. No command-line arguments are accepted.
- Uses only the standard-library modules json, math, and sys. The program performs no filesystem operations.
- Reads at most 65537 bytes from sys.stdin.buffer and rejects input exceeding 65536 bytes. UTF-8 decoding is strict.
- Requires a JSON array containing only objects; an empty array is valid. Rejects malformed JSON, duplicate keys at every depth, nonstandard numeric constants, and float tokens that convert to infinity.
- Successful input produces exactly one JSON object on stdout, exits 0, and produces no stderr. Fields are sorted by Python string ordering; type counts cover only immediate field values and omit zero counts.
- Invalid input exits 2 with a fixed error message on stderr and no stdout. Diagnostics do not disclose input values or produce a traceback.

## Steps

- Save the example as summarize.py.
- Prepare a UTF-8 JSON array of objects, at most 65536 bytes.
- Run: python3 summarize.py < records.json
- Inspect records and the sorted fields array. Present counts records containing the field; missing is the remaining record count.
- Handle exit code 2 as invalid or unreadable input.

## Checks

- Six independent CLI fixtures passed in offline CPython 3.12.15 Docker.
- Checked mixed types, empty collections, missing and Unicode fields, container types, non-object records and duplicate keys.
- Seven additional unittest methods passed in the same pinned Python image, including byte boundaries, invalid UTF-8, non-finite numbers, nested duplicate keys, invalid structure, extra arguments and a long integer.

## Limits

- Reports observed field presence and value types, not an inferred schema or a guarantee about future data.
- Nested values are parsed and validated, but their internal fields and types are not summarized.
- Input values are not printed; field names are included as required.
- Integer tokens use an internal integer placeholder because only their type matters. This avoids Python's integer-conversion digit limit without changing the report.
- Excessive nesting or resource exhaustion is rejected with a generic error. Floating-point conversion follows Python semantics, including finite rounding and underflow.
- The entire input and parsed values are held in memory. Memory use can exceed the input byte size.
- Standard input may block while waiting for data or EOF. The byte limit is not a timeout.
- Output write failures are outside the input-validation error guarantee.
- Field names can themselves contain sensitive information; inspect the report before sharing it.

## Example input

```text
[{"name":"Ana","active":true},{"name":"José","age":30}]
```

## Expected output

```text
{"records":2,"fields":[{"name":"active","present":1,"missing":1,"types":{"boolean":1}},{"name":"age","present":1,"missing":1,"types":{"number":1}},{"name":"name","present":2,"missing":0,"types":{"string":2}}]}
```

## Recorded validation scope

Six independent CLI fixtures and seven additional boundary-test methods passed in pinned, offline CPython 3.12.15 Docker. These checks do not establish exhaustive correctness, performance for arbitrary inputs, or behavior on other Python versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/json.html
- https://docs.python.org/3.12/library/sys.html
- https://docs.python.org/3.12/library/math.html
