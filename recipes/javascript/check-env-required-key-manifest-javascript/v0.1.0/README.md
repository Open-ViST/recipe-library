# Audit required configuration keys without exposing values with JavaScript

Report missing and empty required names, duplicate assignment positions and unknown keys under one literal assignment contract.

Published recipe: [check-env-required-key-manifest-javascript](https://openvist.com/recipes/check-env-required-key-manifest-javascript/)

**Language:** javascript · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.cjs`

node recipe.cjs < input.txt

## Requirements

- Save as audit.js and run with Node.js 22: node audit.js < input.txt. Supply no command-line arguments. The CLI reads only descriptor 0 and requires only node:fs.
- Input consists of selector names, exactly one literal --- separator line, then literal KEY=value assignments. Exactly empty lines and lines starting with # are ignored. Whitespace is never trimmed.
- Keys must match ASCII [A-Za-z_][A-Za-z0-9_]{0,63}. Selectors must be unique. Assignments split at the first equals sign; all remaining characters are literal value content.
- Successful output is exactly one JSON object followed by LF, with missing, empty, duplicates and unknown fields. Key-name arrays and duplicate entries use ASCII key ordering. Duplicate positions are one-based assignment-record ordinals.
- A required key is empty if any of its assignments has an exactly empty value. Unknown names are distinct assigned keys absent from the selectors. Values are never emitted.
- Invalid input, arguments, UTF-8 or stdin reads produce empty stdout, exactly error: invalid input followed by LF on stderr, and exit status 2. Successful execution exits 0 with empty stderr.
- Example stdin: A\nB\n---\nA=\nA=literal\nC=x\n
- Expected example stdout: {"missing":["B"],"empty":["A"],"duplicates":[{"key":"A","positions":[1,2]}],"unknown":["C"]} followed by LF.

## Steps

- Save the example as recipe.cjs.
- Prepare input.txt with selectors, a --- separator and literal assignments; use synthetic values while learning.
- Run the documented command and inspect the JSON output.
- Exit 2 indicates rejected input; no successful JSON result is emitted.

## Checks

- Check the supplied example against its expected output.
- Inspect missing, empty, duplicate and unknown key findings.
- Confirm invalid syntax and extra arguments fail without input values in diagnostics.

## Limits

- Reads at most 65537 bytes total and rejects input longer than 65536 bytes.
- Requires strict UTF-8 without a leading BOM. Rejects ASCII controls other than LF, including CR, NUL and DEL.
- Allows at most 100 selector records and 100 assignment records, counting duplicate assignments separately.
- The combined UTF-8 byte length of every assignment value, including duplicates, must not exceed 1024 bytes.
- This is a literal LF-only protocol, not general dotenv syntax. It performs no interpolation, escaping, quote removal or inline-comment processing.
- No files, environment variables, network resources or subprocesses are accessed by the CLI. Output-write and allocation failures are outside the input-error guarantee.
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

- https://nodejs.org/docs/latest-v22.x/api/fs.html
- https://nodejs.org/api/globals.html#class-textdecoder
