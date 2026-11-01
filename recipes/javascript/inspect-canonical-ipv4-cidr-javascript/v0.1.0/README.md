# Inspect IPv4 CIDR network boundaries with JavaScript

Calculate network boundaries, inclusive last addresses and address counts from saved IPv4 CIDR strings without enumerating hosts.

Published recipe: [inspect-canonical-ipv4-cidr-javascript](https://openvist.com/recipes/inspect-canonical-ipv4-cidr-javascript/)

**Language:** javascript · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.cjs`

node recipe.cjs < input.txt

## Requirements

- Save as recipe.cjs and run node recipe.cjs < input.txt with no CLI arguments. Supply LF-separated IPv4 CIDR records on stdin.
- Requires Node.js 22 CommonJS with no dependencies. Uses node:fs only for bounded stdin reads and stdout/stderr writes, and TextDecoder imported from node:util.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Uses fatal UTF-8 decoding with ignoreBOM:true, then explicitly rejects a leading BOM.
- Ignores exactly empty lines, accepts at most 100 nonempty records, and preserves input order and duplicates. Empty input returns {"networks":[]}. All input is validated before success output.
- Each nonempty record must be one canonical IPv4/prefix string: four decimal octets in 0..255 and a decimal prefix in 0..32, with no leading zeros except the single digit 0. Whitespace, comments, CR, non-ASCII characters and malformed records are rejected.
- Uses exact integer arithmetic, Math.floor and powers of two without bitwise operations or host enumeration. Each result contains exactly input, network, last, prefix, address_count and host_bits_set.
- Success emits exactly one compact JSON object followed by LF, exits 0 and leaves stderr empty. Invalid input, extra arguments, decoding errors and stdin read failures exit 2 with empty stdout and exactly error: invalid input followed by LF on stderr.

## Steps

- Save the example as recipe.cjs.
- Create input.txt with records in the documented exact format.
- Run the documented command; inspect the JSON result.
- Exit 2 means rejected input; no partial successful output is emitted.

## Checks

- Compare the supplied example with its expected output.
- Check /0, /31 and /32, inclusive boundaries and malformed-input rejection.
- Review the recorded test evidence before adapting the code.

## Limits

- Offline stdin/stdout CLI only; no files opened by path, environment inspection, network, DNS, subprocesses or dynamic execution.
- Accepts IPv4 CIDR records only; no membership syntax, IPv6, wildcard masks, netmask spellings, hostnames, URL forms or implicit normalization.
- Host bits are accepted and reported. The last address is inclusive, and address counts include every bit pattern, not just usable hosts: /0 contains 4294967296 addresses and /32 contains 1.
- Does not classify routability, private/public trust, reachability, security or device availability.
- Output-write and allocation failures are outside the input-error guarantee.
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
- https://nodejs.org/api/fs.html
- https://nodejs.org/api/util.html#class-utiltextdecoder
