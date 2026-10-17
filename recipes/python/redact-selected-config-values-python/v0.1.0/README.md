# Redact selected configuration assignment values with Python

Replace every value assigned to an explicit selected key while preserving the order and literal values of unselected assignments.

Published recipe: [redact-selected-config-values-python](https://openvist.com/recipes/redact-selected-config-values-python/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.py`

python3 recipe.py < input.txt

## Requirements

- Save the code as redact.py and run with Python 3.12 using no CLI arguments: python3.12 redact.py. Supply the protocol text through standard input.
- Uses only sys and json. Performs one bounded stdin read of 65537 bytes, rejects input exceeding 65536 bytes, and strictly decodes UTF-8.
- Requires exactly one literal --- separator line. Rejects a leading BOM and prohibited controls anywhere. Ignores only empty lines and lines starting with #; whitespace is not trimmed.
- Validates ASCII key syntax, unique selectors, at most 100 selectors, at most 100 assignment records, and at most 1024 total UTF-8 bytes across original assignment values, including duplicates and selected values.
- Preserves assignment order, duplicate assignments, and all unselected values. Replaces every selected assignment value, including an empty value, with [REDACTED].
- Validates the complete input before producing successful stdout. Success writes exactly one JSON object followed by LF using ensure_ascii=True, exits 0, and leaves stderr empty. Invalid input, arguments, UTF-8, or stdin read failure produces only error: invalid input followed by LF on stderr and exits 2.
- No output key-name arrays are produced; assignment records remain in input order.

## Steps

- Save the example as recipe.py.
- Prepare input.txt with selectors, a --- separator and literal assignments; use synthetic values while learning.
- Run the documented command and inspect the JSON output.
- Exit 2 indicates rejected input; no successful JSON result is emitted.

## Checks

- Check the supplied example against its expected output.
- Check all selected duplicate values are replaced; review unselected values before sharing.
- Confirm invalid syntax and extra arguments fail without input values in diagnostics.

## Limits

- This is a literal LF-only assignment protocol, not a general dotenv parser. Quotes, backslashes, spaces, # characters within values, and additional = characters are preserved literally.
- Only explicitly selected keys are redacted. Unselected values remain visible; this is neither automatic secret detection nor certification that output is safe to publish.
- The CLI reads no files, environment variables, credentials, or host configuration and performs no network access, subprocess execution, or dynamic execution.
- Output-write and allocation failures are outside the input-error guarantee.
- Literal assignment subset only; no quoting rules, export syntax, interpolation, multiline values or general dotenv compatibility.
- Unselected assignment values are emitted unchanged. Review output before sharing.
- stdin may block until EOF; input is bounded to 65536 bytes and 100 selector / 100 assignment records. Total assignment-value bytes are limited to 1024.

## Example input

```text
TOKEN
---
TOKEN=secret-one
HOST=localhost
TOKEN=secret-two

```

## Expected output

```text
{"assignments":[{"key":"TOKEN","value":"[REDACTED]"},{"key":"HOST","value":"localhost"},{"key":"TOKEN","value":"[REDACTED]"}]}
```

## Recorded validation scope

The release gate requires six primary fixtures and 29 supplementary checks in the pinned offline runtime. Review the bound test evidence for the actual release; these checks do not prove exhaustive correctness or compatibility with other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/sys.html
- https://docs.python.org/3.12/library/json.html
