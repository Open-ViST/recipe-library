# Measure UTF-8 byte and scalar widths of text lines with Rust

Report storage length and Unicode scalar count per nonempty line without confusing either measure with display width.

Published recipe: [measure-utf8-line-widths-rust](https://openvist.com/recipes/measure-utf8-line-widths-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe
- Run recipe with text supplied on stdin. No CLI arguments are accepted, including help flags.
- Reads at most 65537 bytes from stdin and rejects input exceeding 65536 bytes. Requires strict UTF-8, rejects a leading UTF-8 BOM, and rejects every CR character.
- Splits only on LF and discards exactly empty segments. Preserves all other text, order, whitespace, and duplicates without trimming or normalization.
- Validates at most 100 nonempty lines and at most 256 UTF-8 bytes per retained line before computing scalar counts.
- Successful execution exits 0, emits exactly one JSON object followed by a newline, and emits no stderr. Empty input or input containing only LF characters produces {"widths":[]}.
- Invalid arguments, invalid input, and stdin-read failures exit 2 with no stdout and exactly error: invalid input followed by a newline on stderr, subject to the output-failure limitation below. Diagnostics never contain input values.
- Uses only the standard library, explicit std::io imports, and permitted fully qualified APIs. No Cargo, external crates, filesystem access, networking, subprocesses, or dynamic loading are used.

## Steps

- Save the example as recipe.rs.
- Compile with Rust 1.99.0 using rustc --edition=2021 recipe.rs -o recipe.
- Prepare UTF-8 input.txt following the documented operation-specific conventions.
- Run ./recipe < input.txt.
- Inspect the JSON result. Exit 2 with exactly error: invalid input followed by a newline on stderr and no stdout identifies rejected input or stdin-read failure. Output-write failures may also exit nonzero, without that diagnostic and potentially after partial stdout; these are outside the input-error guarantee.

## Checks

- The example must produce the documented JSON result.
- Empty stdin must produce the documented empty result.
- Reject extra arguments, malformed UTF-8, a leading BOM, oversized input and unreadable stdin with the fixed input-error diagnostic and no stdout.

## Limits

- The bytes field measures UTF-8 storage bytes excluding LF separators. The scalars field counts Rust .chars(): Unicode scalar values, not grapheme clusters or terminal display columns. Combining marks and components of multi-scalar emoji count separately.
- Only a BOM at the beginning of the entire input is rejected as a BOM. U+FEFF elsewhere is retained and counted. Unicode line separators other than LF remain part of a line.
- Stdin may block until EOF or until the 65537-byte read bound is reached. No timeout is imposed.
- Memory holds up to 65537 input bytes, at most 100 borrowed line references, the serialized JSON, and small temporary numeric strings. Allocator, buffering, and runtime overhead are additional; this is not a strict total-memory cap.
- Successful output reveals line order, the number of nonempty lines, and each line's byte and scalar lengths. These measurements can be sensitive even though text contents are not printed.
- Memory-allocation failures and output-write failures are outside the input-error guarantee. A detected successful-output write or flush failure exits 1; stdout may already be partial. Failed stderr writes can prevent delivery of the prescribed error diagnostic.

## Example input

```text
café
💻
é

```

## Expected output

```text
{"widths":[{"bytes":5,"scalars":4},{"bytes":4,"scalars":1},{"bytes":3,"scalars":2}]}
```

## Recorded validation scope

Six independent CLI fixtures and 16 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
