# Classify ASCII identifier spellings with Rust

Check a local identifier spelling rule independently of compiler keywords and provider naming policies.

Published recipe: [classify-ascii-identifiers-rust](https://openvist.com/recipes/classify-ascii-identifiers-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe
- Run recipe with no arguments and supply input through stdin. Help flags and all other arguments are rejected.
- Reads at most 65537 bytes and rejects inputs exceeding 65536 bytes. Requires strict UTF-8, rejects a leading UTF-8 BOM, and rejects every CR, including CRLF.
- Splits only on LF and discards exactly empty segments. Retains input order without trimming, normalization, grouping or deduplication. Before classification, enforces at most 100 nonempty lines and at most 256 UTF-8 bytes per retained line.
- A spelling is true exactly when it matches the ASCII convention [A-Za-z_][A-Za-z0-9_]*. Keywords are accepted. Other spellings, including non-ASCII text and whitespace-bearing lines, produce false rather than an input error. Empty input produces {"valid":[]}.
- Success exits 0 and writes exactly one JSON object followed by a newline, with no stderr. Invalid arguments, invalid input and stdin-read failures exit 2, emit no stdout, and write exactly error: invalid input followed by a newline to stderr, subject to the failure limitations below.

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

- Stdin can block while waiting for more bytes or EOF. Input within the accepted size bound requires EOF before processing finishes.
- Memory use is O(B + L + R), where B is the bounded input buffer, L is at most 100 borrowed line references, and R is the small JSON result. Buffer capacity and allocator overhead can exceed the logical input size.
- Successful output reveals the number, order and lexical validity of retained spellings; treat it as potentially sensitive.
- Memory-allocation failures and output-write failures are outside the input-error guarantee. A stdout write or flush failure exits 2 and may leave partial stdout. Failed stderr writes can prevent delivery of the required diagnostic.
- This checks only the stated ASCII spelling convention, independently of compiler keyword rules and provider naming policies. It does not establish provider compatibility, production suitability or uniqueness.

## Example input

```text
name
_x2
2x
x-y
```

## Expected output

```text
{"valid":[true,true,false,false]}
```

## Recorded validation scope

Six independent CLI fixtures and 16 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
