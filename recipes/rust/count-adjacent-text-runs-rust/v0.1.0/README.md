# Count consecutive runs of equal text lines with Rust

Summarize consecutive repetition lengths without merging occurrences separated by another token.

Published recipe: [count-adjacent-text-runs-rust](https://openvist.com/recipes/count-adjacent-text-runs-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0: rustc --edition=2021 recipe.rs -o recipe
- Run recipe with input supplied on stdin and no arguments. Help flags are rejected.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8, rejects a leading UTF-8 BOM, and rejects every CR, including CRLF.
- Splits only on LF and discards exactly empty segments. Whitespace-only lines remain. Retains at most 100 nonempty lines, each at most 256 UTF-8 bytes, validating these limits before grouping.
- Compares retained lines exactly, without trimming or normalization. Discarded empty segments do not interrupt runs; different retained lines do. Empty input produces {"runs":[]}.
- After complete validation, success writes exactly one JSON object followed by a newline, writes no stderr, and exits 0.
- Invalid arguments, invalid input, and stdin-read failures produce no stdout, write exactly error: invalid input followed by a newline to stderr, and exit 2, subject to the failure limitations below.
- Uses only the standard library, permitted imports, stdin/stdout/stderr, argument inspection for rejection, and process exit for status.

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

- Stdin can block while waiting for data or EOF. No timeout is imposed.
- Memory includes a 65537-byte input buffer, capacity for 100 borrowed line references and 100 run lengths, a small JSON buffer, and standard I/O and allocator overhead. Retained line text is not copied.
- Successful output omits line contents but reveals run lengths and repetition structure; treat it as potentially sensitive.
- Memory-allocation failures and output-write failures are outside the input-error guarantee. A detected stdout write or flush failure exits 1 and may leave partial output. Failure to write stderr can prevent delivery of the prescribed diagnostic.

## Example input

```text
a
a
b
a
```

## Expected output

```text
{"runs":[2,1,1]}
```

## Recorded validation scope

Six independent CLI fixtures and 16 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
