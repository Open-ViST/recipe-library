# Redact selected configuration assignment values with JavaScript

Replace every value assigned to an explicit selected key while preserving the order and literal values of unselected assignments.

Published recipe: [redact-selected-config-values-javascript](https://openvist.com/recipes/redact-selected-config-values-javascript/)

**Language:** javascript · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.cjs`

node recipe.cjs < input.txt

## Requirements

- Save the code as redact.cjs and run node redact.cjs with the protocol supplied on stdin. No CLI arguments are accepted. Requires Node.js 22 and only requires node:fs.
- Provide selector keys, exactly one line containing ---, then KEY=value assignments. Empty lines and lines starting with # are ignored without trimming.
- Keys must match ASCII [A-Za-z_][A-Za-z0-9_]{0,63}. Selectors must be unique. At most 100 selectors and 100 assignment records are accepted.
- Input is read from descriptor 0 using readSync with a cumulative maximum of 65537 bytes; inputs larger than 65536 bytes are rejected. Strict UTF-8 decoding retains any BOM so a leading BOM can be explicitly rejected.
- CR, NUL, other ASCII controls except LF, and DEL are rejected everywhere. The total UTF-8 length of original assignment values, including duplicates, must not exceed 1024 bytes.
- The complete input is validated before stdout is written. Success emits exactly one JSON object followed by LF, exits 0, and leaves stderr empty. Invalid arguments, input, UTF-8, or stdin reads produce only error: invalid input followed by LF on stderr and exit 2.
- Example stdin: TOKEN\n---\nTOKEN=example\nLABEL=hello=world\nTOKEN=\n
- Example stdout: {"assignments":[{"key":"TOKEN","value":"[REDACTED]"},{"key":"LABEL","value":"hello=world"},{"key":"TOKEN","value":"[REDACTED]"}]} followed by LF.

## Steps

- Save the example as recipe.cjs.
- Prepare input.txt with selectors, a --- separator and literal assignments; use synthetic values while learning.
- Run the documented command and inspect the JSON output.
- Exit 2 indicates rejected input; no successful JSON result is emitted.

## Checks

- Check the supplied example against its expected output.
- Check all selected duplicate values are replaced; review unselected values before sharing.
- Confirm invalid syntax and extra arguments fail without input values in diagnostics.

## Limits

- This is a literal LF-only protocol, not general dotenv syntax. Quotes, spaces, backslashes, # characters, and additional equals signs in values are literal.
- Only explicitly selected keys are redacted. Unselected values remain in output; this is not automatic secret detection or a safe-to-publish certification.
- Assignment order and duplicates are preserved. No key-name arrays are emitted, so no key-name sorting is applicable.
- There are no file, environment, network, subprocess, or dynamic-execution operations. Filesystem calls only read stdin and write stdout or stderr through their existing descriptors.
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

Release requires six primary fixtures, 29 original supplementary checks and one grouped Unicode regression containing ten full-program runs. Actual evidence must be recorded against the candidate. Bounded checks, not exhaustive proof.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://nodejs.org/docs/latest-v22.x/api/fs.html
- https://nodejs.org/api/globals.html#class-textdecoder
