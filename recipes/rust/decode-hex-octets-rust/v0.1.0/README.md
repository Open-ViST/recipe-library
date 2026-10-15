# Decode lowercase hexadecimal octet lines with Rust

Convert two-character hexadecimal tokens into ordered byte values without interpreting them as text.

Published recipe: [decode-hex-octets-rust](https://openvist.com/recipes/decode-hex-octets-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe
- Run ./recipe with input supplied through stdin. No CLI arguments are accepted, including help flags.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8, rejects a leading UTF-8 BOM, and rejects every CR.
- Splits only at LF and discards exactly empty segments. Before token classification, enforces at most 100 nonempty lines and at most 256 UTF-8 bytes per retained line. No trimming or normalization occurs.
- Each retained line must be exactly two lowercase ASCII hexadecimal digits. Preserves order and duplicates, converting tokens into integer byte values without interpreting decoded bytes as text.
- Empty input or input consisting only of LF characters produces {"bytes":[]}. Successful output is one JSON object followed by a newline, with exit status 0 and no stderr.
- All input validation completes before successful stdout is written. Invalid arguments, invalid input, and stdin-read failures produce no stdout, exit 2, and write exactly error: invalid input followed by a newline to stderr, subject to the output-failure limitation below.
- Uses only the standard library and permitted APIs; no Cargo, external crates, filesystem access, networking, or subprocesses.

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

- Memory use is bounded by the 65537-byte input buffer, up to 100 borrowed line references and 100 decoded bytes, a JSON output buffer of at most 412 bytes, and standard-library buffering and allocation overhead.
- Reading stdin may block while waiting for data or EOF. Inputs of 65536 bytes or fewer require EOF to establish completion.
- Successful output contains decoded input values and may be sensitive. Error diagnostics never include input values.
- Memory-allocation failures and output-write failures are outside the input-error guarantee. Output-write failures may leave partial stdout or prevent the fixed stderr diagnostic from being delivered; detected stdout-write failures exit 2.

## Example input

```text
00
ff
7f
00

```

## Expected output

```text
{"bytes":[0,255,127,0]}
```

## Recorded validation scope

Six independent CLI fixtures and 17 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
