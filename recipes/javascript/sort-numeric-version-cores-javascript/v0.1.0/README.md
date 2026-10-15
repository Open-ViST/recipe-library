# Sort numeric version cores with JavaScript

Sort bounded major.minor.patch version cores numerically without claiming full semantic-version support.

Published recipe: [sort-numeric-version-cores-javascript](https://openvist.com/recipes/sort-numeric-version-cores-javascript/)

**Language:** javascript · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.cjs`

node recipe.cjs < input.json

## Requirements

- Save the code as recipe.cjs and run node recipe.cjs using Node.js 22. Supply the JSON array through stdin, then end stdin. No command-line arguments are accepted, including help options.
- Example stdin: ["2.0.0","1.10.0","1.2.0"]. Output: {"versions":["1.2.0","1.10.0","2.0.0"]}.
- Input must be strict UTF-8 JSON. The decoder preserves a leading BOM so JSON.parse rejects it. Native JSON.parse semantics apply, including ordinary JSON whitespace and string escape decoding.
- The parsed input must be an array of at most 100 ASCII version strings. Each decoded string must contain exactly three dot-separated decimal components, each from 0 through 999999, without leading zeros except for 0 itself.
- Versions are compared numerically by major, then minor, then patch. Original decoded strings and duplicates are preserved. An empty array produces {"versions":[]}.
- Successful execution exits 0 naturally, writes exactly one JSON object followed by a newline to stdout, and writes nothing to stderr. Invalid arguments, invalid input, or stdin read failures exit 2 with no stdout and the generic lowercase stderr diagnostic error: invalid input.

## Steps

- Use Node.js 22 CommonJS. Save the code as recipe.cjs.
- Save the supplied JSON example as input.json, encoded as UTF-8 without a BOM.
- Run: node recipe.cjs < input.json
- Compare the output with the expected result; handle exit code 2 as invalid input.

## Checks

- The supplied example must match the documented JSON output.
- Error cases must exit 2 with no stdout. Review sensitive successful output before sharing it.

## Limits

- Only node:fs is required. Input is read exclusively from stdin using bounded readSync calls; no input paths are opened, files written, external commands executed, or network operations performed.
- The program reads at most 65537 bytes and rejects input exceeding 65536 bytes. It may block waiting for stdin data or EOF.
- Input is held in memory: a 65537-byte buffer, decoded text, the parsed JSON value, sorting records, and serialized output. The 100-record limit applies after parsing; there is no streaming JSON parser.
- This sorts bounded numeric version cores only, not full semantic versions. Prerelease identifiers, build identifiers, signs, embedded whitespace, version ranges, and package resolution are unsupported.
- Successful output repeats the supplied version strings and may therefore contain sensitive input data. Error diagnostics do not disclose input values.
- Output-write failures are outside the exit-status and diagnostic guarantees.

## Example input

```text
["1.10.0", "2.0.0", "1.2.3"]
```

## Expected output

```text
{"versions": ["1.2.3", "1.10.0", "2.0.0"]}
```

## Recorded validation scope

Six independent CLI fixtures and 10 curated supplementary checks passed in the pinned offline Node.js 22 CommonJS container. This does not establish exhaustive correctness, production performance or compatibility with an external provider.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://nodejs.org/docs/latest-v22.x/api/fs.html
- https://nodejs.org/download/release/v22.23.3/docs/api/util.html
