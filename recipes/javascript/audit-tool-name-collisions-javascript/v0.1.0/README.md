# Find case-insensitive collisions in tool names with JavaScript

Audit tool identifiers under an explicit local ASCII naming convention and report collisions after lowercase normalization.

Published recipe: [audit-tool-name-collisions-javascript](https://openvist.com/recipes/audit-tool-name-collisions-javascript/)

**Language:** javascript · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `audit-tools.cjs`

node audit-tools.cjs < names.json

## Requirements

- Save as audit-tools.cjs and run with Node.js 22: node audit-tools.cjs. Supply one JSON array through stdin, then signal EOF. No CLI arguments or help option are accepted.
- Uses only node:fs, solely for bounded, read-only reads from stdin. Reads at most 65537 bytes and rejects input exceeding 65536 bytes before JSON parsing.
- Decodes strict UTF-8 with global TextDecoder and fatal:true. Native JSON.parse syntax rules apply, including rejection of a preserved leading BOM.
- Accepts only strings of 1–64 ASCII characters: an initial letter followed by letters, digits, underscores or hyphens. An empty array is valid.
- Successful output is one JSON object containing normalized names in original order and collisions sorted by ASCII name, with ascending one-based positions. Map-based counting safely handles constructor and prototype.
- Valid input exits 0 without stderr. Invalid arguments, stdin errors or invalid input exit 2 with a generic diagnostic on stderr and no stdout, traceback or input values.

## Steps

- Use Node.js 22. Save the CommonJS example as audit-tools.cjs.
- Save a UTF-8 JSON array of names as names.json, at most 65536 bytes.
- Run: node audit-tools.cjs < names.json
- Inspect normalized names and collision positions. Resolve collisions before integrating the names with your own application.

## Checks

- For the supplied example, lookup collides at positions 1 and 2.
- Inspect the naming convention and compare it with your application requirements.
- Handle exit code 2 as invalid input or arguments. Successful output contains the names.

## Limits

- This is an audit under a local naming convention, not a guarantee of compatibility with any AI provider. It does not execute tools.
- The entire parsed input and generated output are held in memory. Stdin can block until EOF.
- Successful output contains names, which may be sensitive.
- Output-write failures are outside the input-validation error guarantee.
- Use the provider-specific documentation separately when integrating a real tool API.

## Example input

```text
["Lookup","lookup","Send"]
```

## Expected output

```text
{"normalized":["lookup","lookup","send"],"collisions":[{"name":"lookup","positions":[1,2]}]}
```

## Recorded validation scope

Six independent CLI fixtures and ten curated supplementary checks passed in pinned offline Node.js 22 Docker, including stdin read errors and leading-BOM rejection. These checks do not establish exhaustive correctness or compatibility with any tool provider.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://nodejs.org/docs/latest-v22.x/api/fs.html
- https://nodejs.org/download/release/v22.23.3/docs/api/util.html
