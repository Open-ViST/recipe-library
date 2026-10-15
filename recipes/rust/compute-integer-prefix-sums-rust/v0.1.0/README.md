# Compute bounded integer prefix sums with Rust

Accumulate each numeric prefix in input order using a representation wide enough for the maximum total.

Published recipe: [compute-integer-prefix-sums-rust](https://openvist.com/recipes/compute-integer-prefix-sums-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe
- Run ./recipe with input supplied through stdin. No CLI arguments are accepted, including help flags. Only the standard library is used.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8, rejects a leading UTF-8 BOM, and rejects every CR.
- Splits only on LF and discards exactly empty segments. Before numeric classification, enforces at most 100 nonempty lines and at most 256 UTF-8 bytes per retained line. No trimming, normalization, sorting, or deduplication occurs.
- Each retained line must be canonical ASCII decimal in 0..1000000, without signs, spaces, or leading zeroes except for 0 itself.
- Accumulates prefixes in input order using u64. The maximum total is 100000000. Empty input or input containing only LF characters produces {"sums":[]}.
- After complete validation, success writes exactly one JSON object followed by a newline, writes no stderr, and exits 0.
- Invalid arguments, invalid input, or stdin-read failures produce no stdout, attempt to write exactly error: invalid input followed by a newline to stderr, and exit 2. Diagnostics never include input values.

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

- Memory use is O(B + L + J), where B is the bounded input buffer, L is at most 100 retained-line references and prefix sums, and J is the small generated JSON string. Allocator capacity and standard I/O buffering add overhead.
- Stdin can block while awaiting more data or EOF. The read cap prevents consuming more than 65537 bytes but does not impose a time limit.
- Successful output contains every prefix sum and can reveal the original values through differences; treat it as sensitive when the input is sensitive.
- Memory-allocation failures and output-write failures, including stderr-write failures, are outside the input-error guarantee. A stdout-write failure can leave partial output; the program exits 2 without adding a diagnostic.
- The program reads only stdin and writes only stdout/stderr. It performs no filesystem access, networking, subprocess execution, or dynamic loading.

## Example input

```text
2
0
3
1
```

## Expected output

```text
{"sums":[2,2,5,6]}
```

## Recorded validation scope

Six independent CLI fixtures and 18 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
