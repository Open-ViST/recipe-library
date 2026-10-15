# Sort and deduplicate line-separated port numbers with Rust

Convert a small LF-separated list of canonical decimal port numbers into a sorted, deduplicated JSON array.

Published recipe: [audit-port-number-lines-rust](https://openvist.com/recipes/audit-port-number-lines-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc --edition=2021 recipe.rs -o recipe
./recipe < ports.txt

## Requirements

- Save the code as recipe.rs and compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe
- Run ./recipe < ports.txt without command-line arguments, supplying LF-separated port numbers on stdin.
- Uses only the standard library, reads only stdin, and writes only stdout or stderr.
- Validates all input before writing exactly one sorted, deduplicated JSON object followed by a newline.
- Success exits 0 without stderr. Invalid arguments, invalid input, or stdin read failure exit 2 with exactly error: invalid input followed by a newline on stderr and no stdout.
- Do not interpret exit 2 alone as input rejection. Input or argument rejection and stdin read failure are identified by the exact stderr diagnostic "error: invalid input\n". Detected stdout write or flush failures also exit 2, but without that diagnostic and potentially after partial stdout output.

## Steps

- Save the example as recipe.rs.
- Compile with Rust 1.99.0 using rustc --edition=2021 recipe.rs -o recipe.
- Prepare an LF-separated UTF-8 ports.txt using canonical decimal numbers.
- Run ./recipe < ports.txt.
- Inspect the sorted ports array. Exit 2 with exactly error: invalid input followed by a newline on stderr and no stdout identifies an input or stdin-read failure. Detected output-write or flush failures also exit 2, but without that diagnostic and potentially after partial stdout; these are outside the input-error guarantee.

## Checks

- The example must output ports 22, 80 and 443 exactly once in numeric order.
- An empty input returns an empty ports array.
- Reject 01, 65536, signs, whitespace, CRLF, malformed UTF-8, excessive bytes and more than 100 nonempty lines with exit 2 and no stdout.

## Limits

- Reads at most 65537 bytes and rejects input exceeding 65536 bytes.
- Requires strict UTF-8 without a leading UTF-8 BOM.
- Accepts at most 100 nonempty lines before deduplication; exactly empty lines, including the final empty segment after LF, are ignored.
- Each nonempty line must be canonical ASCII decimal in 0..65535. CRLF, whitespace-only lines, leading or trailing whitespace, signs, decimal points, non-ASCII digits, and leading zeroes other than the single digit 0 are rejected.
- Empty input produces {"ports":[]} followed by a newline.
- Output-write failures and memory allocation failures are outside the diagnostic guarantee. Detected output-write failures exit 2 without an input-error diagnostic and may leave partial output.
- This operates on supplied port numbers only; it makes no network request, connection test, availability claim or security assessment.

## Example input

```text
80
443
80
22

```

## Expected output

```text
{"ports":[22,80,443]}
```

## Recorded validation scope

Six independent CLI fixtures and 22 supplementary cases are executed in pinned, offline Rust 1.99.0 containers. These checks do not establish exhaustive correctness or behavior on other versions.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/collections/struct.BTreeSet.html
- https://doc.rust-lang.org/std/primitive.u16.html
