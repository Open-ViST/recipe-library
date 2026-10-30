# Inspect IPv4 CIDR network boundaries with Rust

Calculate network boundaries, inclusive last addresses and address counts from saved IPv4 CIDR strings without enumerating hosts.

Published recipe: [inspect-canonical-ipv4-cidr-rust](https://openvist.com/recipes/inspect-canonical-ipv4-cidr-rust/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

rustc recipe.rs -O -o recipe && ./recipe < input.txt

## Requirements

- Save the source as recipe.rs and compile with Rust 1.99.0 using: rustc --edition=2021 recipe.rs -o recipe
- Run recipe without arguments. Supply LF-separated IPv4 CIDR records through stdin; the program reads no files and uses only the standard library.
- Input is limited to 65536 bytes and 100 nonempty records. The bounded reader consumes at most 65537 bytes to detect oversized input.
- Every nonempty record must be exactly a canonical IPv4 address followed by / and a canonical decimal prefix from 0 through 32. Host bits are accepted. Empty lines are ignored; whitespace is not trimmed.
- Successful execution writes exactly one compact JSON object followed by LF, preserves record order and duplicates, exits 0, and leaves stderr empty. Empty input produces {"networks":[]}.
- Invalid arguments, invalid input, UTF-8 errors and stdin read failures produce no stdout, write exactly error: invalid input followed by LF to stderr, and exit 2.

## Steps

- Save the example as recipe.rs.
- Create input.txt with records in the documented exact format.
- Run the documented command; inspect the JSON result.
- Exit 2 means rejected input; no partial successful output is emitted.

## Checks

- Compare the supplied example with its expected output.
- Check /0, /31 and /32, inclusive boundaries and malformed-input rejection.
- Review the recorded test evidence before adapting the code.

## Limits

- Only IPv4 CIDR records are supported. Spaces, CR, tabs, NUL, comments, BOMs, non-ASCII text, leading zeros, signs, extra slashes and alternate address spellings are rejected.
- Calculations use u64 arithmetic without enumerating addresses. A /0 contains 4294967296 addresses; a /32 contains one.
- address_count includes every bit pattern in the CIDR block and is not usable-host capacity. host_bits_set only indicates whether the supplied address differs from its network boundary.
- No routability, trust, reachability, security or device-availability classification is performed.
- Output-write and allocation failures are outside the input-error guarantee. A detected stdout write failure exits 2 and may leave partial stdout.
- IPv4 text only; no DNS, sockets, IPv6, firewall configuration or security/routability assessment.
- LF-only ASCII input, at most 65536 bytes and 100 nonempty records. Blank lines ignored; duplicates retained.
- Address counts include all bit patterns, not usable hosts.

## Example input

```text
192.0.2.129/24

```

## Expected output

```text
{"networks":[{"input":"192.0.2.129/24","network":"192.0.2.0","last":"192.0.2.255","prefix":24,"address_count":256,"host_bits_set":true}]}
```

## Recorded validation scope

The release gate requires six primary fixtures and 29 supplementary checks in the pinned offline runtime. Actual passing evidence must be recorded for this candidate before approval. This does not prove exhaustive correctness or portability to every runtime.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://www.rfc-editor.org/rfc/rfc4632
- https://doc.rust-lang.org/std/io/trait.Read.html
- https://doc.rust-lang.org/std/primitive.u64.html
