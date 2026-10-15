# Distinguish LF CRLF and bare CR endings with Rust

Count newline representations in supplied text while treating CRLF as one paired ending.

Published recipe: [count-line-ending-forms-rust](https://openvist.com/recipes/count-line-ending-forms-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe
- Run recipe without arguments and supply the complete text on stdin. All arguments, including help flags, are rejected.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8 and rejects a leading UTF-8 BOM. Validation finishes before successful stdout begins.
- Scans left to right, consuming each CRLF pair as one ending. Remaining LF and bare CR are counted separately. Ordinary characters and other Unicode line separators are not counted; an unterminated final segment adds no ending.
- Success exits 0 and writes exactly {"lf":n,"crlf":n,"cr":n} followed by a newline, with no stderr.
- Invalid arguments, invalid input, or non-interrupted stdin-read failures exit 2, emit no stdout, and write exactly error: invalid input followed by a newline to stderr, subject to the output-write limitation below. Diagnostics never include input values.

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

- Uses a fixed 65537-byte input buffer plus small constant bookkeeping and standard-library I/O overhead. Runtime is linear in the input size; there is no line-count limit.
- Stdin may block while waiting for data or EOF. Exactly 65536 bytes still require EOF to establish that the input is within the limit.
- Empty input is valid and produces zero counts. A UTF-8 BOM occurring anywhere other than the beginning is ordinary text.
- Successful output reveals newline counts, which may be sensitive metadata.
- Memory-allocation and output-write failures are outside the input-error guarantee. A stdout write or flush failure exits 2 and may leave partial stdout; a failed stderr write may prevent the required diagnostic.
- This counts literal newline forms; it does not parse records or normalize a document.

## Example input

```text
a
b
c
```

## Expected output

```text
{"lf":1,"crlf":1,"cr":1}
```

## Recorded validation scope

Six independent CLI fixtures and 11 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
