# Compare two JSON objects and report changed paths with Python

Find added, removed and changed JSON object paths without fetching an API or altering either input.

Published recipe: [compare-json-object-paths-python](https://openvist.com/recipes/compare-json-object-paths-python/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `compare_json.py`

python3 compare_json.py before.json after.json

## Requirements

- Python 3.12 on Linux; standard library only.
- Two UTF-8 regular files containing top-level JSON objects.
- At most 1 MiB per file. Final-component symlinks are rejected.

## Steps

- Save the example code as compare_json.py.
- Save the original object as before.json and the new object as after.json.
- Run: python3 compare_json.py before.json after.json
- Inspect the added, removed and changed arrays. Validation errors exit with code 2.

## Checks

- Six independent fixtures passed in an offline CPython 3.12.15 Docker container.
- Checked identical objects, additions/removals, nested changes, escaped paths, boolean-versus-number arrays and duplicate-key rejection.
- The fixture input files remained unchanged.

## Limits

- Linux-specific open flags. Rejects final-component symlinks, directories and non-regular files. Intermediate directories may contain symlinks; use trusted paths. This is not a host filesystem sandbox.
- Deeply nested inputs or unusually long integer literals may exceed Python runtime limits and are rejected with exit 2.
- Integers and finite floats use Python numeric equality, so 1 and 1.0 compare equal. Floating-point parsing follows Python's rounding behavior.
- Both documents are parsed in memory. Memory use can exceed their combined file sizes.
- This output is a difference summary, not a JSON Patch or a lossless reconstruction.
- Arrays are atomic: a changed element reports the array path, not its index.
- Added or removed objects report their own path without expanding descendants.

## Example input

```text
before.json: {"name":"A","enabled":true}
after.json: {"name":"B","enabled":true,"count":2}
```

## Expected output

```text
{"added": ["/count"], "removed": [], "changed": ["/name"]}
```

## Recorded validation scope

Six independent CLI fixtures passed in pinned, offline CPython 3.12.15 Docker. Additional Linux regression checks passed as part of the VPS test suite, covering size boundaries, invalid JSON, non-finite values and non-regular files. This does not establish behavior on other operating systems or exhaustive correctness.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/json.html
- https://docs.python.org/3.12/library/os.html
- https://docs.python.org/3.12/library/stat.html
- https://www.rfc-editor.org/rfc/rfc6901
