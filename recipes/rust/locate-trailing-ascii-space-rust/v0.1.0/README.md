# Locate trailing spaces and tabs in text lines with Rust

Find retained lines ending in ASCII space or tab without trimming other Unicode whitespace.

Published recipe: [locate-trailing-ascii-space-rust](https://openvist.com/recipes/locate-trailing-ascii-space-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs
- Run the compiled executable with no arguments and supply text through stdin. All arguments, including help flags, are rejected.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8, rejects a leading UTF-8 BOM, and rejects every CR, including CRLF.
- Splits only on LF and discards exactly empty segments. Retains at most 100 nonempty lines, each at most 256 UTF-8 bytes. These limits are checked before classification.
- Outputs one-based retained-line indices for lines whose final character is ASCII space U+0020 or tab U+0009. Other Unicode whitespace does not qualify. No trimming, normalization, grouping, or deduplication occurs.
- Successful execution exits 0, writes exactly one JSON object followed by a newline, and writes nothing to stderr. Empty input or no matching lines produces {"positions":[]}.
- Invalid arguments, invalid input, and stdin-read failures exit 2 with no stdout and exactly error: invalid input followed by a newline on stderr, subject to the output-write limitation below. Diagnostics never disclose input values.

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

- Stdin can block while awaiting more bytes or EOF; no timeout is implemented. Input below the read bound must reach EOF before processing completes.
- Memory use is proportional to the bounded input buffer, plus up to 100 borrowed line references, a small result string, and standard-library I/O buffering. Lines are not copied.
- Successful output can reveal sensitive information through matching positions and their relationship to retained input lines.
- Memory-allocation failures and output-write failures are outside the input-error guarantee. A detected stdout write or flush failure exits 1 and may leave partial stdout; failure to write an error diagnostic can prevent its delivery.
- Uses only the standard library and accesses only stdin, stdout, stderr, argument presence, and exit status. No filesystem, network, subprocess, or dynamic-loading operations are performed.

## Example input

```text
a 
b
c	
```

## Expected output

```text
{"positions":[1,3]}
```

## Recorded validation scope

Six independent CLI fixtures and 16 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
