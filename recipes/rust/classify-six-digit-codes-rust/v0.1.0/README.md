# Classify fixed-width six-digit ASCII codes with Rust

Validate a width-sensitive decimal code convention while preserving the meaning of leading zeroes.

Published recipe: [classify-six-digit-codes-rust](https://openvist.com/recipes/classify-six-digit-codes-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile using Rust 1.99.0: rustc --edition=2021 recipe.rs -o recipe
- Run recipe with input supplied on stdin and no CLI arguments. Help flags are rejected.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8, rejects a leading UTF-8 BOM, and rejects every CR byte, including CRLF.
- Splits only on LF and discards exactly empty segments. Retains at most 100 nonempty lines, each at most 256 UTF-8 bytes. All limits are enforced before classification; no trimming, normalization, grouping or deduplication occurs.
- Each retained line produces one boolean, in input order. Only exactly six ASCII digits are valid. Leading zeroes are preserved and accepted; no numeric parsing occurs. Other spellings within the input limits produce false.
- Success exits 0, emits exactly one JSON object of the form {"valid":[boolean,...]} followed by a newline, and writes no stderr. Empty input or only LF characters produces {"valid":[]}.
- Invalid arguments, invalid input and stdin-read failures exit 2 with no stdout and exactly error: invalid input followed by a newline on stderr, subject to the output-write limitation below. Diagnostics do not contain input values.

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

- Memory use is bounded by a 65537-byte input buffer, storage for at most 100 borrowed line references, a JSON output buffer of at most 612 bytes, and standard I/O and allocation overhead.
- Stdin can block while waiting for input or EOF. There is no timeout. Reading stops and rejects immediately once 65537 bytes have been obtained.
- Successful output can be sensitive: it reveals the number and ordering of retained lines and their validity classifications, although it does not echo their contents.
- Memory-allocation failures and output-write failures are outside the input-error guarantee. A detected stdout write or flush failure exits 1 and may leave partial stdout; stderr failures can prevent delivery of the complete error diagnostic.
- Uses only the standard library, stdin, stdout and stderr, plus argument inspection solely to reject arguments and process exit solely to set status. No filesystem, network, subprocess or dynamic-loading access is used.

## Example input

```text
000000
123456
12345
1234567
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
