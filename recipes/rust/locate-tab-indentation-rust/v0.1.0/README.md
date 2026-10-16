# Locate leading tab indentation in text lines with Rust

Distinguish a tab at the beginning of a retained line from tabs appearing after another character.

Published recipe: [locate-tab-indentation-rust](https://openvist.com/recipes/locate-tab-indentation-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < input.txt

## Requirements

- Save as recipe.rs and compile with Rust 1.99.0: rustc --edition=2021 recipe.rs -o recipe
- Run recipe with text supplied on stdin. No CLI arguments are accepted, including help flags.
- The CLI reads at most 65537 bytes and rejects input exceeding 65536 bytes. Input must be strict UTF-8 without a leading UTF-8 BOM or any CR character.
- Only LF splits lines. Exactly empty segments are discarded; whitespace-only segments remain. There may be at most 100 retained lines, each containing at most 256 UTF-8 bytes. All limits are validated before classification.
- A retained line qualifies only when its first Unicode scalar is U+0009 (TAB). A space followed by a tab does not qualify. No text is trimmed, normalized, grouped or deduplicated.
- Success exits 0, emits exactly one JSON object followed by a newline, and emits no stderr. The positions array contains one-based retained-line indices in input order. Empty input or no qualifying lines produces {"positions":[]}.
- Invalid arguments, invalid input and stdin-read failures exit 2 without stdout and emit exactly error: invalid input followed by a newline on stderr, subject to the output-failure limitation below. Diagnostics never contain input values.
- The implementation uses only the standard library, stdin, stdout and stderr, plus argument inspection solely to reject arguments and process exit solely to set status.

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

- Stdin can block while waiting for more data or EOF. The reader stops once it has consumed 65537 bytes; a valid-length stream normally requires EOF before processing finishes.
- Memory use consists primarily of the bounded input buffer, up to 100 borrowed line references, and a small JSON output buffer. Allocator bookkeeping and allocation capacity may add overhead.
- Successful output reveals which retained lines begin with tabs and may therefore disclose sensitive structural information. Handle or redirect it appropriately.
- Memory-allocation failures and output-write failures, including stderr failures, are outside the input-error guarantee. A stdout write or flush failure exits 2 and may leave partial stdout; error diagnostics cannot be guaranteed when stderr itself fails.

## Example input

```text
	item
 item
 	item
item	
```

## Expected output

```text
{"positions":[1]}
```

## Recorded validation scope

Six independent CLI fixtures and 16 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.str.html
- https://doc.rust-lang.org/std/primitive.u32.html
