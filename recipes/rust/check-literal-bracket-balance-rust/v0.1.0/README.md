# Check literal bracket nesting in text lines with Rust

Validate matched round square and curly brackets while treating all other scalars as ordinary text.

Published recipe: [check-literal-bracket-balance-rust](https://openvist.com/recipes/check-literal-bracket-balance-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs. Compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe
- Run with no arguments, supplying text on stdin: ./recipe < input.txt. All arguments, including help flags, are rejected.
- Reads at most 65537 bytes from stdin and rejects input exceeding 65536 bytes. Requires strict UTF-8, rejects a leading UTF-8 BOM, and rejects every CR, including CRLF.
- Splits only on LF and discards exactly empty segments. Whitespace-only segments remain. Before bracket classification, rejects more than 100 retained lines or any retained line exceeding 256 UTF-8 bytes. No trimming, normalization, grouping, or deduplication occurs.
- Checks each retained line independently with a stack for (), [] and {}. Every other Unicode scalar is ordinary text, including quotes, backslashes, and any non-leading BOM. Wrong closers and unmatched brackets produce false.
- Success exits 0 and writes exactly one JSON object followed by LF, with no stderr. Empty input or input containing only LF characters produces {"balanced":[]}.
- Invalid arguments, invalid input, and stdin-read failures exit 2 without stdout and report exactly error: invalid input followed by LF on stderr, subject to the allocation and output-failure limitations below. Diagnostics never contain input values.

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

- Stdin can block while waiting for data or EOF. No timeout is provided. The read bound limits bytes consumed, not elapsed time.
- Memory use is bounded by the input buffer holding at most 65537 bytes, references to at most 100 lines, a temporary stack of at most 256 characters, and the small JSON output buffer. Allocator capacity and standard-library I/O buffering add overhead.
- Successful output does not reproduce line text, but reveals the number and order of retained lines and their bracket-balance results; treat that information as potentially sensitive.
- Memory-allocation failures and stdout/stderr write or flush failures are outside the input-error guarantee. An output failure may leave partial output or prevent the diagnostic from being delivered; detected stdout failures exit 2.
- Uses only the standard library, stdin, stdout, and stderr. Argument inspection is used only to reject arguments, and process exit is used only to set status. No filesystem, networking, subprocess, dynamic-loading, or unsafe operations are used.
- This checks literal brackets, not programming-language syntax or quoted-string semantics.

## Example input

```text
([])
([)]
plain
```

## Expected output

```text
{"balanced":[true,false,true]}
```

## Recorded validation scope

Six independent CLI fixtures and 16 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
