# Partition bounded integers by parity with Rust

Separate even and odd values while preserving order and duplicates within each partition.

Published recipe: [partition-integer-parity-rust](https://openvist.com/recipes/partition-integer-parity-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe
- Run ./recipe without arguments, supplying input on stdin. All arguments, including help flags, are rejected.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8, rejects a leading UTF-8 BOM, and rejects every CR.
- Splits only on LF and discards exactly empty segments. Before parsing values or partitioning, enforces at most 100 retained lines and at most 256 UTF-8 bytes per retained line. Nothing is trimmed or normalized.
- Accepts only canonical ASCII decimal integers from 0 through 1000000, with no signs, whitespace, or leading zeroes except the single digit 0.
- Validates the complete input before constructing successful output. Emits exactly one compact JSON object followed by a newline, with even and odd arrays preserving input order and duplicates. Zero is even; empty input produces {"even":[],"odd":[]}.
- Success exits 0 without stderr. Invalid arguments, invalid input, and stdin-read failures exit 2 with no stdout and exactly error: invalid input followed by a newline on stderr, subject to the failure limitations below.
- Uses only the standard library, permitted explicit imports, argument inspection solely to reject arguments, and process exit solely for status.

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

- Stdin can block while waiting for more bytes or EOF. For oversized input, only the first 65537 bytes need be consumed.
- Memory use is O(B + N), where B is the bounded input byte count and N is the number of retained values. It stores the input buffer, at most 100 borrowed line references, at most 100 integers, and the bounded output string; allocator capacity and runtime overhead are additional.
- Successful output contains every accepted numeric value, including duplicates, and may expose sensitive data.
- Memory-allocation failures and output-write failures are outside the input-error guarantee. Successful-output write or flush failures exit 1 and may leave partial stdout. A stderr-write failure can prevent delivery of the required error diagnostic.

## Example input

```text
3
2
0
3
4
```

## Expected output

```text
{"even":[2,0,4],"odd":[3,3]}
```

## Recorded validation scope

Six independent CLI fixtures and 18 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
