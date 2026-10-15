# Classify lowercase SHA-256 hexadecimal spellings with Rust

Check digest text shape without computing hashes or asserting provenance and integrity.

Published recipe: [classify-sha256-spellings-rust](https://openvist.com/recipes/classify-sha256-spellings-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe
- Run recipe without arguments, supplying input through stdin. All arguments, including help flags, are rejected.
- The reader consumes at most 65537 bytes and rejects input exceeding 65536 bytes. Input must be strict UTF-8, must not begin with a UTF-8 BOM, and must contain no CR characters.
- Only LF splits lines. Exactly empty segments are discarded, including those caused by consecutive or trailing LF characters. No trimming or normalization occurs.
- All retained lines are validated before classification: at most 100 nonempty lines, each at most 256 UTF-8 bytes. Duplicate lines remain separate and in input order.
- Each retained line produces true exactly when its bytes are 64 ASCII characters from 0-9 and a-f. Other spellings produce false rather than rejecting the input, provided the input-level limits are satisfied.
- Success exits 0 and writes exactly one JSON object followed by LF, with no stderr. Empty input or input containing only LF characters produces {"valid":[]}.
- Invalid arguments, invalid input, or stdin-read failures exit 2 with no stdout and exactly error: invalid input followed by LF on stderr, subject to the allocation and output-failure limitations below.
- Uses only the standard library, with explicit imports from std::io. The only environment and process calls are argument inspection through std::env::args_os and exit-status selection through std::process::exit.

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

- Stdin may block until EOF or until the 65537-byte read bound is reached. There is no timeout.
- Memory use is bounded by the input and line limits: a 65537-byte input buffer, at most 100 borrowed line references, a small output string, and standard-library buffering and allocator overhead. This is not an exact process-memory ceiling.
- Successful output can be sensitive: it reveals the number and order of retained lines and which satisfy the spelling rule. Input values are not included in error diagnostics.
- Memory-allocation failures and output-write failures are outside the input-error guarantee. A stdout write or flush failure exits 2 without an added diagnostic and may leave partial stdout. A stderr failure can prevent delivery of the required error message.
- This checks textual shape only. It does not compute hashes, verify provenance or integrity, establish uniqueness, or assert provider compatibility or production suitability.
- Text shape does not establish that a hash was computed correctly or that data is trustworthy.

## Example input

```text
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
0000000000000000000000000000000000000000000000000000000000000000
abc
```

## Expected output

```text
{"valid":[true,true,false]}
```

## Recorded validation scope

Six independent CLI fixtures and 17 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
