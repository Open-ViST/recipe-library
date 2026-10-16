# Group repeated exact text tokens by position with Rust

Report positional groups of repeated lines using exact scalar values without printing token contents.

Published recipe: [group-repeated-token-positions-rust](https://openvist.com/recipes/group-repeated-token-positions-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe
- Run with no arguments and supply input on stdin. All arguments, including help flags, are rejected.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8, rejects a leading UTF-8 BOM, and rejects every CR.
- Splits only on LF and discards exactly empty segments. Retains whitespace-only lines unchanged. Allows at most 100 retained lines, each at most 256 UTF-8 bytes, and validates these limits before grouping.
- Positions are one-based indices in the retained nonempty-line sequence, not physical input line numbers. Exact equality uses no trimming, case folding, or Unicode normalization; valid UTF-8 byte equality is equivalent to equality of Unicode scalar sequences.
- Outputs only groups occurring at least twice. Positions ascend within each group, and groups are ordered by their first position. Empty input or input without repeats produces {"groups":[]}.
- Success exits 0 with exactly one JSON object and a newline on stdout and no stderr. Invalid arguments, invalid input, or stdin-read failures exit 2 with no stdout and exactly error: invalid input followed by a newline on stderr, subject to output-write failures.

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

- Stdin may block while waiting for EOF or the 65537-byte read bound. There is no timeout.
- Memory holds the bounded input, at most 100 borrowed line references, grouping metadata for at most 100 positions, and the complete output. Grouping uses quadratic line comparisons, bounded by the 100-line and 256-byte limits.
- Successful output contains no token contents, but duplicate relationships and positions can still reveal sensitive information.
- Memory-allocation failures and output-write failures are outside the input-error guarantee. A detected successful-output write or flush failure exits 1 and may leave partial stdout; a failed diagnostic write may prevent the complete error message from appearing.
- Uses only the standard library, stdin, stdout, and stderr, with argument inspection solely to reject arguments and process exit solely for exit status. No filesystem access or external dependencies are used.

## Example input

```text
a
b
a
b
c
```

## Expected output

```text
{"groups":[[1,3],[2,4]]}
```

## Recorded validation scope

Six independent CLI fixtures and 16 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
