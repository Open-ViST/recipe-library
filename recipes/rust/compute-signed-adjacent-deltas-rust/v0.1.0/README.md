# Compute signed deltas between adjacent integers with Rust

Measure consecutive changes with subtraction in a signed type so decreases remain negative.

Published recipe: [compute-signed-adjacent-deltas-rust](https://openvist.com/recipes/compute-signed-adjacent-deltas-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe
- Run recipe without any arguments, including help flags, and supply input through stdin.
- Uses only the standard library, with an explicit std::io import. No Cargo, crates, filesystem access, networking, subprocesses, unsafe code or dynamic loading.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8, rejects a leading UTF-8 BOM, and rejects every CR.
- Splits only on LF and discards exactly empty segments. Before numeric classification, rejects more than 100 retained lines or any retained line exceeding 256 UTF-8 bytes. Does not trim, normalize, group or deduplicate.
- Accepts only canonical ASCII decimal integers from 0 through 1000000: no signs, spaces or leading zeroes except the spelling 0.
- Computes each adjacent difference as an i64 subtraction, preserving negative decreases. Empty input and a single value produce {"deltas":[]}.
- Success exits 0 and writes exactly one JSON object followed by a newline, with no stderr. Invalid arguments, invalid input and stdin-read failures exit 2 with no stdout and exactly error: invalid input followed by a newline on stderr, subject to the output-write limitations below.

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

- Stdin may block while waiting for data or EOF. The byte bound is not a timeout.
- Memory stores at most 65537 input bytes, 100 retained-line references, 100 i64 values and a small output string. There are at most 99 deltas, each in -1000000..1000000; successful output is at most 904 bytes. Allocation capacities and runtime overhead are additional.
- Successful output reveals the number of adjacent pairs and their signed changes, which may be sensitive. Error diagnostics do not disclose input values.
- Memory-allocation failures and stdout/stderr write or flush failures are outside the input-error guarantee. Output failures can leave partial output; detected stdout failures exit 2 without an additional diagnostic.

## Example input

```text
5
2
2
9
```

## Expected output

```text
{"deltas":[-3,0,7]}
```

## Recorded validation scope

Six independent CLI fixtures and 19 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
