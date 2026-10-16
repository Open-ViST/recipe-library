# Locate breaks in strictly increasing integer sequences with Rust

Report where a number fails to increase relative to its immediate predecessor.

Published recipe: [locate-nonincreasing-steps-rust](https://openvist.com/recipes/locate-nonincreasing-steps-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe
- Run recipe without arguments, supplying input through stdin. Help flags and all other arguments are rejected.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8, rejects a leading UTF-8 BOM, and rejects every CR.
- Splits only at LF and discards exactly empty segments. Before numeric interpretation, enforces at most 100 retained lines and at most 256 UTF-8 bytes per retained line. No trimming or normalization occurs.
- Each retained line must be canonical ASCII decimal from 0 through 1000000, with no sign, whitespace, or leading zeroes except the single digit 0.
- Returns one-based retained-line positions starting at position 2 where the value is less than or equal to its immediate predecessor. Duplicates count as breaks; order is preserved.
- Empty input or input containing only LF bytes returns {"positions":[]}.
- Success exits 0 and writes exactly one JSON object plus a newline, with no stderr. Invalid arguments, invalid input, and stdin-read failures exit 2 with no stdout and exactly error: invalid input followed by a newline on stderr, subject to the failure limitations below.
- Uses only the standard library, with no Cargo dependencies, filesystem access, networking, subprocesses, unsafe code, or dynamic loading.

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

- Stdin may block until EOF, a read failure, or the 65537-byte read bound is reached. No timeout is provided.
- Memory use is O(B + L), where B is the bounded input size and L is the retained-line count. Storage includes the input buffer, up to 100 borrowed line references, up to 100 integers, the output string, and allocator or I/O overhead.
- All input validation finishes before successful stdout is emitted. Memory-allocation failures and output-write failures, including failure to write an error diagnostic, are outside the input-error guarantee. A failed stdout write may leave partial output.
- Successful output reveals sequence-break positions and may be sensitive. Error diagnostics never include input values.

## Example input

```text
1
2
2
0
5
```

## Expected output

```text
{"positions":[3,4]}
```

## Recorded validation scope

Six independent CLI fixtures and 18 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
