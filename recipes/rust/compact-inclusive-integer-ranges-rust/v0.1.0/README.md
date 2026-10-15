# Compact bounded integers into inclusive consecutive ranges with Rust

Summarize present values as maximal runs after numeric sorting and deduplication.

Published recipe: [compact-inclusive-integer-ranges-rust](https://openvist.com/recipes/compact-inclusive-integer-ranges-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe. Run ./recipe with input on stdin. No arguments are accepted, including help flags.
- Uses only the standard library, with explicit imports from std::io. std::env::args_os is used only to reject arguments; std::process::exit is used only for exit status.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8, rejects a leading UTF-8 BOM, and rejects every CR byte, including CRLF.
- Splits only at LF and discards exactly empty segments. Before numeric parsing, sorting or deduplication, enforces at most 100 retained lines and at most 256 UTF-8 bytes per retained line. Nothing is trimmed or normalized.
- Each retained line must contain canonical ASCII decimal in 0..1000000. Signs, whitespace, non-ASCII digits and leading zeroes other than the single spelling 0 are rejected.
- Sorts numerically, removes duplicates and emits maximal consecutive ranges with inclusive endpoints in ascending order. Singletons use equal endpoints. These are present ranges, not missing gaps.
- Empty input or input containing only LF bytes produces {"ranges":[]}. Successful output is exactly one compact JSON object followed by a newline, with exit status 0 and no stderr.
- Argument errors, invalid input and stdin-read failures produce no stdout, exit with status 2, and write exactly error: invalid input followed by a newline to stderr, subject to the allocation and output-failure limitations below. Diagnostics never contain input values.

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

- Stdin can block while waiting for data or EOF. Input of exactly 65536 bytes requires an additional read attempt to establish EOF; detection of a 65537th byte causes rejection without reading further.
- Memory use includes a fixed 65537-byte stack buffer, vectors holding at most 100 line references, values and ranges, and a small output string. Storage is O(B + L), where B is the bounded input capacity and L is the retained-line count; standard-library buffering and allocation overhead are additional.
- Successful output reveals the accepted distinct values through their ranges and may be sensitive.
- Memory-allocation failures and output-write failures, including stderr failures, are outside the input-error guarantee. A stdout write or flush failure exits 2 without adding a diagnostic and may leave partial stdout.
- The program performs no filesystem access, networking, subprocess execution, dynamic loading or unsafe operations.

## Example input

```text
5
1
2
5
8
6
```

## Expected output

```text
{"ranges":[[1,2],[5,6],[8,8]]}
```

## Recorded validation scope

Six independent CLI fixtures and 19 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
