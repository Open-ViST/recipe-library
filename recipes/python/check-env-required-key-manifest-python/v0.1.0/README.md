# Audit required configuration keys without exposing values with Python

Report missing and empty required names, duplicate assignment positions and unknown keys under one literal assignment contract.

Published recipe: [check-env-required-key-manifest-python](https://openvist.com/recipes/check-env-required-key-manifest-python/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.py`

python3 recipe.py < input.txt

## Requirements

- Save the code as recipe.py. Python 3.12 is required: python3 must resolve to Python 3.12 when running python3 recipe.py < input.txt. Pass no CLI arguments; the shell redirects input.txt to standard input. Only sys and json are imported.
- Write unique required key names before exactly one standalone --- line, then literal KEY=value assignment records. The separator is required even when both sections are empty. Exactly empty lines and lines starting with # are ignored in both sections. Whitespace is never trimmed.
- Keys must match ASCII [A-Za-z_][A-Za-z0-9_]{0,63}. Assignments split only at the first equals sign; values are neither expanded nor interpreted.
- Successful execution emits exactly one JSON object with missing, empty, duplicates and unknown fields, followed by LF, exits 0, and writes nothing to stderr. JSON is serialized with ensure_ascii=True after complete input validation. Key-name arrays and duplicate objects are sorted by ASCII key order.
- Missing keys have no assignment. Empty keys are required keys with at least one exactly empty assignment value, even if another assignment is nonempty. Unknown keys are distinct assigned keys not selected as required. Duplicate reporting includes selected and unselected keys; each object contains key and positions, with ascending one-based assignment-record ordinals excluding selectors, blank lines and comments.
- Invalid arguments, input, UTF-8, or stdin read failures produce exactly error: invalid input followed by LF on stderr, exit 2, and no stdout. Input values are never included in output or diagnostics. Use synthetic values for examples; no secrets or host configuration are needed.

## Steps

- Save the example as recipe.py.
- Prepare input.txt with selectors, a --- separator and literal assignments; use synthetic values while learning.
- Run the documented command and inspect the JSON output.
- Exit 2 indicates rejected input; no successful JSON result is emitted.

## Checks

- Check the supplied example against its expected output.
- Inspect missing, empty, duplicate and unknown key findings.
- Confirm invalid syntax and extra arguments fail without input values in diagnostics.

## Limits

- The CLI reads stdin once using sys.stdin.buffer.read(65537) and rejects input exceeding 65536 bytes. It performs no file, environment, network or subprocess access and does not execute other scripts on import.
- Input must be strict UTF-8 without a leading BOM. LF is the only permitted ASCII control character; CR, NUL, other ASCII controls, and DEL are rejected everywhere. Other Unicode scalar values are allowed in values and comments.
- At most 100 selector records and 100 assignment records are permitted. Selectors must be unique. Duplicate assignments count separately. A final LF creates no record.
- The combined UTF-8 length of all assignment values, including duplicate assignments, must not exceed 1024 bytes.
- This is a literal assignment protocol, not a general dotenv parser. Quotes, backslashes, spaces, additional equals signs, and # within values remain literal.
- Output-write and allocation failures are outside the input-error guarantee.
- Literal assignment subset only; no quoting rules, export syntax, interpolation, multiline values or general dotenv compatibility.
- Key names can themselves be sensitive.
- stdin may block until EOF; input is bounded to 65536 bytes and 100 selector / 100 assignment records. Total assignment-value bytes are limited to 1024.

## Example input

```text
API_KEY
HOST
PORT
---
HOST=
API_KEY=first
API_KEY=second
EXTRA=x

```

## Expected output

```text
{"missing":["PORT"],"empty":["HOST"],"duplicates":[{"key":"API_KEY","positions":[2,3]}],"unknown":["EXTRA"]}
```

## Recorded validation scope

The release gate requires six primary fixtures and 29 supplementary checks in the pinned offline runtime. Review the bound test evidence for the actual release; these checks do not prove exhaustive correctness or compatibility with other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/sys.html
- https://docs.python.org/3.12/library/json.html
