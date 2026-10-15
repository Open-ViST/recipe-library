# Validate Hexadecimal Event IDs and Find Duplicates

Read a JSON array of hexadecimal event ID strings from a UTF-8 file or standard input, validate each value, normalize valid IDs to lowercase without an optional leading `0x`, and report duplicate positions. Do not convert IDs to numbers or claim chain validity.

Published recipe: [validate-hex-event-ids](https://openvist.com/recipes/validate-hex-event-ids/)

**Language:** javascript · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `validate-hex-event-ids.cjs`

Save the code as `validate-hex-event-ids.cjs`, then run `node validate-hex-event-ids.cjs ids.json`. Use `node validate-hex-event-ids.cjs - < ids.json` to read standard input. The program prints a JSON report; it exits 0 when all entries are valid, 2 when one or more entries are invalid, and 1 for usage, file, or JSON parse errors.

## Requirements

- Intended runner: Node.js 22.
- No package installation is required; the recipe uses CommonJS and Node.js built-ins.
- Input must be UTF-8 JSON whose top-level value is an array.

## Steps

- Save the supplied code in a `.cjs` file.
- Prepare a JSON array containing event ID strings and select a file path or `-` for stdin.
- Run the Node.js command and inspect the JSON report and exit status.
- Use the reported positions to correct or review invalid and repeated values.

## Checks

- Run the example fixture and compare the JSON report with the expected output.
- Try entries that vary only by letter case or optional prefix and confirm they are reported as duplicates with one-based positions.
- Try empty strings, non-hex characters, and non-string array members; confirm they are listed by position as invalid.
- Try malformed JSON and a non-array JSON top level; confirm the command writes an actionable error to stderr and exits nonzero.
- Run once with a file path and once with `-` plus piped input to verify both input modes.

## Limits

- The rule accepts one or more hexadecimal digits after an optional case-insensitive `0x` prefix; it does not impose a fixed byte length.
- An empty string and a prefix without following hex digits are invalid.
- Duplicate comparison uses lowercase text with the optional prefix removed; it performs no numeric conversion.
- This validates only textual hexadecimal syntax, not event existence, chain membership, or any chain-specific ID rules.
- The program reads the entire input into memory and is intended for bounded JSON inputs.
- Input values are treated only as data; the program does not execute them or modify files.

## Example input

```text
["0xAb12", "ff00", "0xab12", "G1"]
```

## Expected output

```text
{
  "valid": false,
  "normalized": [
    "ab12",
    "ff00",
    "ab12",
    null
  ],
  "invalid": [
    {
      "position": 4,
      "valueType": "string"
    }
  ],
  "duplicates": [
    {
      "normalizedId": "ab12",
      "firstPosition": 1,
      "duplicatePosition": 3
    }
  ]
}
```

## Recorded validation scope

Executed 6 synthetic local fixture cases in isolated Node.js 22.23.3 on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://nodejs.org/docs/latest-v22.x/api/fs.html
- https://nodejs.org/docs/latest-v22.x/api/process.html
