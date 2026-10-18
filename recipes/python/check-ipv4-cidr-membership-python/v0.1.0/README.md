# Check IPv4 address membership in canonical CIDR ranges with Python

Report inclusive membership for saved address and canonical network pairs without DNS, socket access or changing firewall rules.

Published recipe: [check-ipv4-cidr-membership-python](https://openvist.com/recipes/check-ipv4-cidr-membership-python/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.py`

python3 recipe.py < input.txt

## Requirements

- Run with Python 3.12, for example: python3.12 check_ipv4.py. Supply records through standard input and pass no CLI arguments. Only sys and json are imported.
- Each nonempty line must be exactly ADDRESS NETWORK/PREFIX, with one ASCII space. Exactly empty lines are ignored; whitespace is never trimmed.
- IPv4 octets must be canonical decimal values from 0 through 255. Prefixes must be canonical decimal values from 0 through 32. Leading zeros are forbidden except for the single digit 0.
- Networks must have all host bits zero. Noncanonical networks reject the entire input rather than being normalized.
- Success emits exactly one compact JSON object containing only checks, followed by LF, with exit status 0 and empty stderr. Results preserve record order, duplicates, and original valid spellings.
- Membership includes both endpoints: /31 includes both addresses, /32 includes its exact address, and canonical 0.0.0.0/0 includes every IPv4 address.
- Input errors produce empty stdout, exit status 2, and exactly error: invalid input followed by LF on stderr.

## Steps

- Save the example as recipe.py.
- Create input.txt with records in the documented exact format.
- Run the documented command; inspect the JSON result.
- Exit 2 means rejected input; no partial successful output is emitted.

## Checks

- Compare the supplied example with its expected output.
- Check /0, /31 and /32, inclusive boundaries and malformed-input rejection.
- Review the recorded test evidence before adapting the code.

## Limits

- Reads at most 65537 bytes once and rejects input longer than 65536 bytes. At most 100 nonempty records are accepted; empty input yields {"checks":[]}.
- Requires strict UTF-8 without a leading BOM and ASCII-only records. CR, tabs, NUL, comments, extra spaces, and malformed records are rejected.
- Uses bounded integer arithmetic without enumerating hosts. Range sizes include all bit patterns, not merely usable-host capacity; /0 has 4294967296 addresses and /32 has one.
- Offline stdin/stdout processing only: no file access, environment inspection, network, DNS, subprocesses, dependencies, or firewall changes.
- No IPv6, hostnames, URL forms, wildcard masks, netmask spellings, or implicit normalization. Results make no claims about routability, trust, reachability, security, or device availability.
- Output-write and allocation failures are outside the input-error guarantee.
- IPv4 text only; no DNS, sockets, IPv6, firewall configuration or security/routability assessment.
- LF-only ASCII input, at most 65536 bytes and 100 nonempty records. Blank lines ignored; duplicates retained.
- Network input must have zero host bits. Both network and inclusive last addresses count as members.

## Example input

```text
192.0.2.129 192.0.2.0/24

```

## Expected output

```text
{"checks":[{"address":"192.0.2.129","cidr":"192.0.2.0/24","contains":true}]}
```

## Recorded validation scope

The release gate requires six primary fixtures and 29 supplementary checks in the pinned offline runtime. Actual passing evidence must be recorded for this candidate before approval. This does not prove exhaustive correctness or portability to every runtime.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://www.rfc-editor.org/rfc/rfc4632
- https://docs.python.org/3.12/library/sys.html
- https://docs.python.org/3.12/library/json.html
