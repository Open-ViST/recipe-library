# Classify canonical dotted IPv4 text with Rust

Check decimal address spelling under an explicit rule without DNS resolution or network activity.

Published recipe: [classify-ipv4-octet-text-rust](https://openvist.com/recipes/classify-ipv4-octet-text-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe
- Run ./recipe with input supplied through stdin. No CLI arguments are accepted, including help flags.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8, rejects a leading UTF-8 BOM, and rejects every CR byte.
- Splits only at LF, discards exactly empty segments, and preserves all other text without trimming or normalization. Allows at most 100 nonempty lines, each at most 256 UTF-8 bytes. All validation precedes classification and successful stdout.
- Each retained line produces one boolean in input order. True means exactly four ASCII decimal octets in 0..255, separated by dots, with no leading zeroes except the single digit 0. Signs, spaces, non-ASCII digits, and other address spellings produce false rather than input rejection.
- Special, private, and reserved addresses are classified solely by spelling. No DNS resolution, networking, grouping, or deduplication occurs.
- Success exits 0 and writes exactly one JSON object followed by a newline, with no stderr. Empty input or input containing only LF bytes produces {"valid":[]}.
- Invalid arguments, invalid input, and stdin-read failures exit 2, write no stdout, and emit exactly error: invalid input followed by a newline on stderr, subject to the failure limitations below. Diagnostics never contain input values.

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

- Stdin may block while waiting for EOF or enough bytes to establish that the size limit was exceeded.
- Memory use is bounded by the input-size limit: O(65537) input storage, up to 100 borrowed line references, and at most 612 bytes of JSON output, plus allocator capacity and standard-library I/O overhead. No duplicate line strings are stored.
- Successful output reveals the number and order of nonempty lines and their classification results; treat that information as potentially sensitive.
- Memory-allocation failures and output-write or flush failures are outside the input-error guarantee. Output failures may leave partial output; detected stdout failures exit 2 without attempting an input-error diagnostic. Stderr failures may prevent delivery of the diagnostic.
- Only standard-library facilities are used. The program performs no filesystem access, networking, subprocess creation, dynamic loading, or environment-variable access.
- This checks spelling only, not routing, ownership, public reachability or address safety.

## Example input

```text
127.0.0.1
255.255.255.255
256.0.0.1
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
