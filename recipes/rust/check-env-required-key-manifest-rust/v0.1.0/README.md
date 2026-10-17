# Audit required configuration keys without exposing values with Rust

Report missing and empty required names, duplicate assignment positions and unknown keys under one literal assignment contract.

Published recipe: [check-env-required-key-manifest-rust](https://openvist.com/recipes/check-env-required-key-manifest-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save the code as recipe.rs. Compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe
- Run recipe without arguments and supply the protocol through stdin. The executable reads no files, environment variables, or host configuration.
- Provide unique required-key selectors, one exact --- separator line, then literal KEY=value assignments. Exactly empty lines and lines starting with # are ignored in both sections. Whitespace is never trimmed.
- Keys must match ASCII [A-Za-z_][A-Za-z0-9_]{0,63}. Assignments split at the first equals sign; their values are not interpreted.
- Successful execution emits exactly one JSON object followed by LF, exits 0, and leaves stderr empty. All input is validated before stdout is written.
- Missing, empty, and unknown key arrays use ASCII ordering. Duplicate objects use key order and include every one-based assignment-record position, including duplicates of unknown keys.
- Required keys are reported as empty if any assignment has an exactly empty value. Values are never included in output or diagnostics.
- Invalid arguments or input, invalid UTF-8, and stdin read failures produce only error: invalid input followed by LF on stderr, with empty stdout and exit status 2.
- Example stdin: A\nB\n---\nA=\nA=example\nC=literal=value\n. Expected stdout: {"missing":["B"],"empty":["A"],"duplicates":[{"key":"A","positions":[1,2]}],"unknown":["C"]} followed by LF.

## Steps

- Save the example as recipe.rs.
- Prepare input.txt with selectors, a --- separator and literal assignments; use synthetic values while learning.
- Run the documented command and inspect the JSON output.
- Exit 2 indicates rejected input; no successful JSON result is emitted.

## Checks

- Check the supplied example against its expected output.
- Inspect missing, empty, duplicate and unknown key findings.
- Confirm invalid syntax and extra arguments fail without input values in diagnostics.

## Limits

- Input is at most 65536 bytes; the bounded stdin read requests at most 65537 bytes to detect oversize input.
- Input must be strict UTF-8 without a leading BOM. ASCII controls other than LF, including CR, NUL, and DEL, are rejected everywhere, including comments.
- At most 100 selector records and 100 assignment records are accepted. Assignment records are counted before deduplication. A final LF does not add a record.
- The combined UTF-8 byte length of all assignment values, including duplicates and unknown keys, must not exceed 1024.
- Exactly one separator is required; either section may otherwise be empty.
- This is a literal protocol, not general dotenv syntax: no quoting rules, interpolation, shell expansion, export prefixes, inline comments, or multiline values.
- Other Unicode scalar values are allowed in values and comments. The JSON string encoder preserves Unicode and escapes quotes, backslashes, and U+0000 through U+001F.
- Allocation and output-write failures are outside the input-error guarantee. Output-write failures result in exit status 2 and may leave partial stdout.
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

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/str/fn.from_utf8.html
