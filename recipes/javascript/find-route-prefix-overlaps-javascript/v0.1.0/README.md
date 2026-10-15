# Find segment-boundary prefix overlaps in route paths with JavaScript

Report route pairs where one supplied path contains the other as a segment-boundary prefix.

Published recipe: [find-route-prefix-overlaps-javascript](https://openvist.com/recipes/find-route-prefix-overlaps-javascript/)

**Language:** javascript · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.cjs`

node recipe.cjs < input.json

## Requirements

- Save as recipe.cjs. Usage: node recipe.cjs < input.json. Supply a JSON array through stdin; no CLI arguments or help option are accepted.
- Requires Node.js 22 CommonJS and standard library only. The only loaded module is node:fs, used solely for bounded readSync calls on stdin descriptor 0. The program does not open input paths, write files, execute external commands or contact a network.
- Global TextDecoder uses fatal:true and ignoreBOM:true. Malformed UTF-8 is rejected. A leading UTF-8 BOM is preserved and rejected by JSON.parse. Native JSON.parse semantics apply.
- Each path must match the entire ASCII grammar: /, or slash-separated nonempty segments containing only letters, digits, underscores and hyphens. Only / may end in /. Whitespace, repeated slashes, dots, backslashes and non-ASCII characters are rejected.
- Comparisons are case-sensitive. Equal paths and any pair containing / overlap; otherwise one path must begin with the other followed by /. Output indices are one-based positions in the supplied array, with first < second. Records are ordered by first and then second. An empty array is valid. There are no input integer fields or keyed collections.
- Successful processing exits 0, emits exactly one JSON object followed by a newline, and emits no stderr. Invalid arguments, input or stdin read failures emit no stdout, emit the generic lowercase diagnostic error: invalid input on stderr, and exit 2.

## Steps

- Use Node.js 22 CommonJS. Save the code as recipe.cjs.
- Save the supplied JSON example as input.json, encoded as UTF-8 without a BOM.
- Run: node recipe.cjs < input.json
- Compare the output with the expected result; handle exit code 2 as invalid input.

## Checks

- The supplied example must match the documented JSON output.
- Error cases must exit 2 with no stdout. Review sensitive successful output before sharing it.

## Limits

- Reads at most 65537 bytes and rejects inputs larger than 65536 bytes. Accepts at most 20 paths, each nonempty and at most 120 characters. Produces at most 190 overlap records.
- Uses a fixed 65537-byte read buffer and holds decoded text, parsed input and results in memory. Stdin can block while waiting for EOF.
- Successful output can reveal relationships between sensitive routes, even though it contains indices rather than route strings.
- Output-write failures are excluded from the exit-status and diagnostic guarantees.
- This is a lexical audit, not a router precedence or security analysis. It does not normalize paths, decode URL escapes or model provider integrations. No production suitability or uniqueness is claimed.

## Example input

```text
["/api", "/api/v1", "/apix"]
```

## Expected output

```text
{"overlaps": [{"first": 1, "second": 2}]}
```

## Recorded validation scope

Six independent CLI fixtures and 10 curated supplementary checks passed in the pinned offline Node.js 22 CommonJS container. This does not establish exhaustive correctness, production performance or compatibility with an external provider.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://nodejs.org/docs/latest-v22.x/api/fs.html
- https://nodejs.org/download/release/v22.23.3/docs/api/util.html
