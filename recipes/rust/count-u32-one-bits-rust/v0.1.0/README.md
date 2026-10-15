# Count set bits in canonical unsigned 32-bit values with Rust

Report population counts for supplied decimal integers without confusing textual digits with binary representation.

Published recipe: [count-u32-one-bits-rust](https://openvist.com/recipes/count-u32-one-bits-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe. No Cargo or external crates are needed.
- Run recipe without arguments, including help flags, and supply input through stdin.
- At most 65537 bytes are read from stdin; input exceeding 65536 bytes is rejected. Input must be strict UTF-8 without a leading BOM or any CR character.
- Only LF separates lines. Exactly empty segments are discarded; nothing is trimmed or normalized. Before numeric interpretation, retained input is limited to 100 nonempty lines of at most 256 UTF-8 bytes each.
- Each retained line must contain canonical ASCII decimal for a u32: 0 through 4294967295, without signs, whitespace or leading zeroes except the single digit 0.
- After complete validation, successful output is exactly one JSON object followed by a newline, with binary population counts in input order. Empty input or input containing only LF characters produces {"ones":[]}. Success exits 0 with no stderr.
- Invalid arguments, invalid input and stdin-read failures exit 2 without stdout and attempt to write exactly error: invalid input followed by a newline to stderr. Diagnostics never contain input values.

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

- Stdin can block while waiting for bytes or EOF. An input of exactly 65536 bytes requires EOF to establish that no additional byte exists.
- Memory use is bounded in terms of input: at most 65537 input bytes, up to 100 borrowed line references and 100 counts, and at most 311 bytes of successful JSON text. Allocator capacity, temporary formatting storage and standard I/O buffering add overhead.
- Successful output can be sensitive: it reveals each retained value's population count, their order and the number of retained values.
- Memory-allocation failures and output-write failures are outside the input-error guarantee. A detected stdout write or flush failure exits 1 and may leave partial output. A failed stderr write can prevent the complete error diagnostic from appearing.

## Example input

```text
0
1
3
8
4294967295
```

## Expected output

```text
{"ones":[0,1,2,1,32]}
```

## Recorded validation scope

Six independent CLI fixtures and 18 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
