# Count ASCII letter digit whitespace and other bytes with Rust

Summarize an ASCII stream into four disjoint character classes without echoing its content.

Published recipe: [count-ascii-byte-classes-rust](https://openvist.com/recipes/count-ascii-byte-classes-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile using Rust 1.99.0: rustc --edition=2021 recipe.rs -o recipe
- Run recipe without any arguments, including help flags, and supply the complete input through stdin.
- Reads at most 65537 bytes from stdin and rejects input exceeding 65536 bytes. Accepts empty input. Validates strict UTF-8, rejects a leading UTF-8 BOM, and requires ASCII only before writing successful stdout.
- Counts ASCII A-Z and a-z as letters, 0-9 as digits, and only bytes 9, 10, 12, 13 and 32 as whitespace. Every other ASCII byte, including byte 11 and NUL, counts as other.
- Treats stdin as one stream without line splitting, newline normalization or a retained-line count limit. CR and LF each contribute one whitespace byte.
- Success exits 0 and writes exactly one JSON object followed by a newline, with letters, digits, whitespace and other fields, and no stderr.
- Invalid arguments, invalid input and non-interrupted stdin-read failures exit 2 without stdout and attempt to write exactly error: invalid input followed by a newline to stderr. Interrupted reads are retried.
- Uses only the standard library, with no Cargo dependencies, filesystem access, networking, subprocesses or dynamic loading.

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

- Uses a fixed 65537-byte stack buffer plus constant-size counters and standard I/O overhead. Processing time is linear in the bytes read.
- Stdin may block while awaiting data or EOF. An input of exactly 65536 bytes requires EOF to establish acceptance; reading a 65537th byte establishes rejection immediately.
- Successful output does not echo input, but the four counts reveal total length and character-class distribution and may be sensitive.
- Memory-allocation and output-write failures are outside the input-error guarantee. Successful-output write or flush errors cause exit 2 and may leave partial stdout. A failing stderr write can prevent delivery of the required diagnostic.

## Example input

```text
Az09 	
!?
```

## Expected output

```text
{"letters":2,"digits":2,"whitespace":3,"other":2}
```

## Recorded validation scope

Six independent CLI fixtures and 11 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
