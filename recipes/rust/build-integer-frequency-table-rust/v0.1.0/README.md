# Build sorted integer frequency tables with Rust

Count repeated bounded numeric values and arrange their counts by numeric key.

Published recipe: [build-integer-frequency-table-rust](https://openvist.com/recipes/build-integer-frequency-table-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0: rustc --edition=2021 recipe.rs -o recipe. Uses only the standard library, without Cargo or external crates.
- Run recipe with no arguments, including no help flag. Supply input through stdin.
- Reads at most 65537 bytes and rejects input longer than 65536 bytes, stdin-read failures, invalid UTF-8, a leading UTF-8 BOM, and every CR.
- Splits only at LF and discards exactly empty segments. Before numeric parsing or grouping, enforces at most 100 retained lines and at most 256 UTF-8 bytes per retained line. No trimming or normalization occurs.
- Each retained line must contain canonical ASCII decimal in 0..1000000. Signs, whitespace, non-ASCII digits, and leading zeroes other than the single digit 0 are rejected.
- Success exits 0 with no stderr and writes exactly one JSON object followed by a newline. Its frequencies array contains each distinct numeric value once, in ascending numeric order, with counts of retained lines. Empty input or input containing only LF produces {"frequencies":[]}.
- Invalid arguments, invalid input, and stdin-read failures exit 2 without stdout and attempt to write exactly error: invalid input followed by a newline to stderr. Diagnostics never contain input values.

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

- Stdin may block while waiting for EOF or until the 65537-byte read bound is reached.
- Memory use is O(B + L + D), where B is buffered input of at most 65537 bytes, L is at most 100 retained lines, and D is at most 100 distinct values. This includes line references, parsed values, the ordered frequency table, and the output buffer; allocator overhead and capacity rounding add overhead.
- Successful output exposes every distinct input value and its count and may therefore be sensitive.
- Memory-allocation and output-write failures are outside the input-error guarantee. Allocation failure may terminate the program. A detected stdout write or flush failure exits 2 without an added diagnostic and may leave partial stdout; a stderr failure may prevent the complete error diagnostic from being written.

## Example input

```text
2
1
2
0
1
```

## Expected output

```text
{"frequencies":[[0,1],[1,2],[2,2]]}
```

## Recorded validation scope

Six independent CLI fixtures and 18 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
