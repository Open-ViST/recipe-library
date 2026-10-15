# Compare declared permission sets with JavaScript

Report added, removed and unchanged permission labels between two supplied sets.

Published recipe: [compare-permission-sets-javascript](https://openvist.com/recipes/compare-permission-sets-javascript/)

**Language:** javascript · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.cjs`

node recipe.cjs < input.json

## Requirements

- Save the code as recipe.cjs and run node recipe.cjs with Node.js 22. Supply JSON through stdin and finish with EOF. No CLI arguments, including help options, are accepted.
- Input must be a JSON object containing before and after arrays. For example: {"before":["read","write"],"after":["read","share"]}. Additional fields are ignored.
- Each array may contain at most 100 entries. Every entry must be a nonempty string of at most 80 JavaScript UTF-16 code units. Empty arrays are allowed.
- Spelling, whitespace and case are preserved. Identical strings collapse into one Set entry. Each output array is sorted using JavaScript's default UTF-16 string order.
- Successful processing exits normally with status 0, emits exactly one JSON object followed by a newline, and emits no stderr. Invalid arguments, invalid input and stdin read failures exit 2 with no stdout and the generic lowercase stderr diagnostic error: invalid input.
- Only node:fs readSync is used for stdin reads. The CLI does not open input paths, write files, run external commands or contact a network.

## Steps

- Use Node.js 22 CommonJS. Save the code as recipe.cjs.
- Save the supplied JSON example as input.json, encoded as UTF-8 without a BOM.
- Run: node recipe.cjs < input.json
- Compare the output with the expected result; handle exit code 2 as invalid input.

## Checks

- The supplied example must match the documented JSON output.
- Error cases must exit 2 with no stdout. Review sensitive successful output before sharing it.

## Limits

- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. UTF-8 decoding is strict. A leading UTF-8 BOM is preserved by the decoder and rejected by JSON.parse.
- Native JSON.parse semantics apply, including handling of duplicate object keys. There are no integer fields in the required schema; ignored additional fields are not validated.
- The input buffer, decoded text, complete parsed input, permission sets and output are held in memory. Memory use is greater than the input byte limit and depends on the parsed JSON structure.
- Synchronous stdin reads can block while waiting for data or EOF.
- Successful output contains supplied permission labels and may be sensitive. The CLI does not redact those labels.
- Output-write failures are excluded from the stated exit-status and diagnostic guarantees.
- This compares declared labels only. It does not determine effective permissions, authorize actions or provide a provider integration.

## Example input

```text
{"before": ["read", "write"], "after": ["read", "execute"]}
```

## Expected output

```text
{"added": ["execute"], "removed": ["write"], "unchanged": ["read"]}
```

## Recorded validation scope

Six independent CLI fixtures and 10 curated supplementary checks passed in the pinned offline Node.js 22 CommonJS container. This does not establish exhaustive correctness, production performance or compatibility with an external provider.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://nodejs.org/docs/latest-v22.x/api/fs.html
- https://nodejs.org/download/release/v22.23.3/docs/api/util.html
