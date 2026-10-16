# Locate Unicode replacement characters in text lines with Rust

Find already-present U+FFFD markers without mistaking valid UTF-8 decoding for evidence of original data quality.

Published recipe: [locate-replacement-scalars-rust](https://openvist.com/recipes/locate-replacement-scalars-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe
- Run ./recipe with input supplied through stdin. No command-line arguments are accepted, including help flags.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8, rejects a leading UTF-8 BOM, and rejects every CR character, including CRLF.
- Splits only at LF and discards exactly empty segments. Retains whitespace-only segments without trimming or normalization. Before classification, validates at most 100 retained lines and at most 256 UTF-8 bytes per retained line.
- Successful output is exactly one JSON object followed by a newline, with the form {"positions":[1,3]}. Positions are ascending, one-based indices among retained nonempty lines. Each matching line appears once, regardless of its number of U+FFFD characters. Empty input or no matching lines produces {"positions":[]}.
- All input validation finishes before successful stdout is written. Success exits 0 without stderr. Invalid arguments, invalid input, or stdin-read failures exit 2 with no stdout and exactly error: invalid input followed by a newline on stderr, subject to the failure limitations below.

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

- Memory use is bounded independently of input length: a 65537-byte stack buffer, a small output string and temporary index strings, plus standard-library I/O buffers and runtime overhead. Lines are borrowed from the input buffer rather than copied.
- Stdin may block while waiting for data or EOF. Input of exactly 65536 bytes requires a subsequent read to establish EOF; observing a 65537th byte immediately establishes oversize input.
- Only already-present U+FFFD markers are located. Valid UTF-8 decoding neither establishes original data quality nor reveals whether a marker was intentional or introduced earlier. Malformed UTF-8 is rejected, never decoded with replacement.
- Successful output reveals matching retained-line positions and may itself be sensitive. Error diagnostics do not disclose input values.
- Memory-allocation failures and output-write failures, including stderr failures, are outside the input-error guarantee. A stdout-write failure attempts exit status 2 and may leave partial output.
- A replacement marker may have been intentionally supplied. This does not recover or diagnose the original encoding.

## Example input

```text
ok
�
x�y

```

## Expected output

```text
{"positions":[2,3]}
```

## Recorded validation scope

Six independent CLI fixtures and 16 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
