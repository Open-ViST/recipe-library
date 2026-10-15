# Count literal equals signs per text line with Rust

Measure delimiter occurrences without interpreting quoted values or assignment syntax.

Published recipe: [count-literal-equals-signs-rust](https://openvist.com/recipes/count-literal-equals-signs-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save the code as recipe.rs. Compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe
- Run recipe with input supplied through stdin and no CLI arguments. All arguments, including help flags, are rejected.
- Reads at most 65537 bytes from stdin and rejects input exceeding 65536 bytes. Requires strict UTF-8, rejects a leading UTF-8 BOM, and rejects every CR character, including CRLF line endings.
- Splits only at LF and discards exactly empty segments. Retains whitespace-only segments unchanged. Before counting, validates that there are at most 100 retained lines and that each contains at most 256 UTF-8 bytes.
- Counts every literal U+003D equals sign in retained-line order, including occurrences inside quoted text. Performs no trimming, normalization, grouping, deduplication, or assignment parsing.
- Success exits 0, emits exactly one JSON object followed by a newline, and emits no stderr. Empty input or input containing only LF characters produces {"counts":[]}.
- Invalid arguments, invalid input, and stdin-read failures exit 2 with no stdout and exactly error: invalid input followed by a newline on stderr, subject to the failure limitations below. Diagnostics never include input values.
- Uses only the standard library, with explicit std::io imports. The only environment/process calls are std::env::args_os for argument rejection and std::process::exit for exit status.

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

- Stdin may block while waiting for data or EOF. Accepted input requires EOF; oversized input is rejected once the 65537th byte is read.
- Application storage includes a fixed 65537-byte input buffer, references to at most 100 retained lines, and a small output string. Overall application memory is O(input bound + retained-line count), plus standard-library buffering and allocator overhead.
- Line lengths are measured in UTF-8 bytes, not Unicode characters. Only a BOM at the beginning of the entire input is rejected as a BOM; later U+FEFF characters are ordinary text.
- Successful output reveals retained-line counts and per-line equals-sign frequencies, which may be sensitive even though original text is not printed.
- Memory-allocation failures and output-write failures are outside the input-error guarantee. A detected stdout write or flush failure exits 2 without an added diagnostic and may leave partial stdout. Stderr failures may prevent delivery of the required error message.

## Example input

```text
a=b
x==y
plain
```

## Expected output

```text
{"counts":[1,2,0]}
```

## Recorded validation scope

Six independent CLI fixtures and 16 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
