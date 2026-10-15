# Classify Unicode scalar palindromes in text lines with Rust

Identify exact reversal symmetry in scalar sequences without applying language-specific normalization.

Published recipe: [classify-scalar-palindromes-rust](https://openvist.com/recipes/classify-scalar-palindromes-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile using Rust 1.99.0: rustc --edition=2021 recipe.rs -o recipe
- Run recipe with no arguments, supplying input through stdin. Help flags and all other arguments are rejected.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8, rejects a leading UTF-8 BOM, and rejects every CR, including CRLF.
- Splits only on LF and discards exactly empty segments. Before classification, enforces at most 100 retained lines and at most 256 UTF-8 bytes per retained line.
- Classifies retained lines in original order by comparing Unicode scalar values forward and backward. Case, spaces, punctuation, and combining characters remain unchanged; there is no trimming, normalization, grouping, deduplication, or grapheme-cluster interpretation.
- On success, exits 0 and writes exactly one JSON object followed by a newline, with no stderr. Empty input or input consisting only of LF characters produces {"palindromes":[]}.
- Invalid arguments, invalid input, and stdin-read failures exit 2 with no stdout and exactly error: invalid input followed by a newline on stderr, subject to the allocation and output-write limitations below. Diagnostics never include input values.
- Uses only the standard library and permitted APIs. No Cargo, external crates, unsafe code, filesystem access, networking, subprocesses, or dynamic loading are used.

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

- Stdin may block while waiting for EOF or enough bytes to reach the 65537-byte read bound.
- Memory use is O(B + L + J), where B is at most 65537 input bytes, L is at most 100 borrowed line references, and J is the small JSON output buffer. Allocation capacities, I/O buffering, and runtime overhead may exceed logical data sizes. Classification does not allocate scalar arrays.
- A BOM is forbidden only at the beginning of the complete input. U+FEFF elsewhere is an ordinary scalar. Only LF separates lines; other Unicode line-separator characters remain part of a line.
- Successful output can reveal sensitive properties of the input, including the number and order of retained lines and each palindrome result. Input bytes remain in process memory until released and are not securely erased.
- Memory-allocation failures and output-write failures are outside the input-error guarantee. A detected stdout write or flush failure exits 2 and may leave partial stdout. Stderr failures may prevent delivery of the complete error diagnostic.
- Scalar reversal is not a linguistic or grapheme-aware palindrome test.

## Example input

```text
aba
abc
💻a💻
```

## Expected output

```text
{"palindromes":[true,false,true]}
```

## Recorded validation scope

Six independent CLI fixtures and 16 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
