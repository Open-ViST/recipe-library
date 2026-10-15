# Count shared leading octets in IPv4 pairs with Rust

Compare canonical address pairs by complete leading octets without inferring subnet masks.

Published recipe: [compare-ipv4-prefix-octets-rust](https://openvist.com/recipes/compare-ipv4-prefix-octets-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile using Rust 1.99.0: rustc --edition=2021 recipe.rs -o recipe. Uses only the standard library, without Cargo or external crates.
- Run recipe with no arguments, including no help flags. Supply input through stdin.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8, rejects a leading UTF-8 BOM, and rejects every CR byte, including CRLF.
- Splits only on LF and discards exactly empty segments. Before parsing any pair, enforces at most 100 nonempty lines and at most 256 UTF-8 bytes per retained line. No trimming, normalization, grouping, or deduplication occurs.
- Each retained line must contain exactly two IPv4 addresses separated by exactly one |. Each address requires four ASCII decimal octets in 0..255, with no signs, whitespace, or leading zeroes except the octet 0.
- Returns one count per retained line in input order. Counts equal complete leading octets until the first difference, from 0 through 4; this is not a CIDR prefix-bit calculation. Empty input or only LF characters produces {"shared":[]}. A final LF is optional.
- Success exits 0 and writes exactly one JSON object followed by LF, with no stderr. Invalid arguments, invalid input, and stdin-read failures exit 2 with no stdout and exactly error: invalid input followed by LF on stderr, subject to the failure limitations below.
- Uses no std::net, filesystem access, networking, subprocesses, unsafe code, external code, or dynamic loading. Argument access is used only to reject arguments, and process exit is used only for exit status.

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

- Memory use is O(B + L), where B is the bounded input size and L is the retained line count. Storage includes an input buffer initially allocated for 65537 bytes, up to 100 borrowed line references, up to 100 counts, and at most 213 bytes of successful JSON output, plus standard-library buffering and allocation overhead.
- Stdin can block while waiting for EOF or the 65537-byte read bound. No timeout is provided.
- All input validation finishes before successful stdout begins. Successful output preserves pair order and reveals address-similarity information, which may be sensitive even though address spellings are not echoed.
- Memory-allocation failures and output-write failures are outside the input-error guarantee. A stdout-write failure may leave partial output and triggers exit status 2. Diagnostic writes are best effort if stderr itself fails.

## Example input

```text
1.2.3.4|1.2.3.5
1.2.3.4|9.2.3.4
```

## Expected output

```text
{"shared":[3,0]}
```

## Recorded validation scope

Six independent CLI fixtures and 18 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
