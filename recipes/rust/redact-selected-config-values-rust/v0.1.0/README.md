# Redact selected configuration assignment values with Rust

Replace every value assigned to an explicit selected key while preserving the order and literal values of unselected assignments.

Published recipe: [redact-selected-config-values-rust](https://openvist.com/recipes/redact-selected-config-values-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe
- Run ./recipe with no arguments and supply the protocol on stdin. The CLI uses only the standard library and reads no files or environment variables.
- Place unique selector keys before exactly one literal --- line, followed by KEY=value assignments. Exactly empty lines and lines beginning with # are ignored; whitespace is never trimmed.
- Keys must match ASCII [A-Za-z_][A-Za-z0-9_]{0,63}. Assignments split at the first =, preserving the remainder literally.
- Example stdin: TOKEN\n---\nTOKEN=example\nMODE=development\n. Here the displayed \n sequences represent LF characters. Output: {"assignments":[{"key":"TOKEN","value":"[REDACTED]"},{"key":"MODE","value":"development"}]} followed by LF.
- The entire input is validated before successful stdout. Success emits exactly one JSON object plus LF, exits 0, and leaves stderr empty. Input errors emit only error: invalid input plus LF on stderr and exit 2.
- Assignment order and duplicate assignments are preserved. There are no output key-name arrays to sort; selector membership is stored in deterministic ASCII order.

## Steps

- Save the example as recipe.rs.
- Prepare input.txt with selectors, a --- separator and literal assignments; use synthetic values while learning.
- Run the documented command and inspect the JSON output.
- Exit 2 indicates rejected input; no successful JSON result is emitted.

## Checks

- Check the supplied example against its expected output.
- Check all selected duplicate values are replaced; review unselected values before sharing.
- Confirm invalid syntax and extra arguments fail without input values in diagnostics.

## Limits

- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8 without a leading BOM.
- Rejects CR, NUL, all other ASCII controls except LF, and DEL everywhere, including comments. Other Unicode scalar values are allowed in values and comments.
- Allows at most 100 unique selector records and 100 assignment records. Duplicate selectors are invalid; duplicate assignments count separately.
- The combined UTF-8 byte length of all original assignment values, including selected values and duplicates, must not exceed 1024 bytes.
- This is a literal LF-only protocol, not general dotenv syntax. It performs no quoting interpretation, interpolation, whitespace normalization, or automatic secret detection.
- Only explicitly selected keys are redacted, including when their original values are empty. Unselected values remain in output; the result is not certified safe to publish.
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

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/str/fn.from_utf8.html
