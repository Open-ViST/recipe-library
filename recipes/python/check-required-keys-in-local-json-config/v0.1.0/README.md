# Check required keys in a local JSON configuration file

Read a local JSON file, compare its top-level object keys with CLI-supplied required keys, and report sorted missing keys without printing any configuration values.

Published recipe: [check-required-keys-in-local-json-config](https://openvist.com/recipes/check-required-keys-in-local-json-config/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `check_config.py`

Save as `check_config.py`. Run `python3.12 check_config.py settings.json --required api_url token`; use `-` instead of the path to read JSON from standard input, for example `printf '{"api_url":"local","token":"hidden"}' | python3.12 check_config.py - --required api_url token`.

## Requirements

- Intended runner: Python 3.12. This states the intended runner, not a tested minimum version.
- Only Python standard-library modules are used: argparse, json, pathlib, and sys.
- The input file must be readable UTF-8 JSON, or JSON may be supplied on stdin using source `-`.
- Required key names are supplied as one or more values after `--required`. Only top-level object keys are checked.

## Steps

- Save the code as `check_config.py`.
- Create a small synthetic JSON object in a local file, including a harmless dummy value for any credential-like key.
- Run the command with `--required` followed by keys that are present and one that is absent.
- Check that the output lists only the absent key names, in sorted order, and contains no values from the JSON.
- Repeat with stdin using `-`, then try empty, malformed, non-object, and nonexistent-file inputs.

## Checks

- With `{ "a": 1, "b": 2 }` and required keys `b c a`, confirm stdout is exactly `missing keys: c` and no values appear.
- With `{ "a": "dummy" }` and required key `a`, confirm stdout is `all required keys are present`.
- With empty input and with malformed text such as `{`, confirm the script reports `error: invalid JSON` to stderr and does not print input text.
- With valid JSON `[]`, `null`, or a string root, confirm it reports `error: JSON root must be an object`.
- Use a nonexistent path and a path containing invalid UTF-8; confirm each produces the generic read error without disclosing file content.
- Pipe valid JSON into source `-` and confirm the same key-check behavior as file input; verify that neither successful nor missing-key output includes JSON values.

## Limits

- This checks key presence only; it does not validate value types, formats, nested keys, or whether a value is safe or usable.
- The script reads the full input into memory; the Python JSON documentation cautions that untrusted JSON can consume substantial CPU and memory, so use appropriately bounded local fixtures.
- Missing keys return exit status 1; input and validation errors return 2; a complete configuration returns 0. No retries are performed.

## Example input

```text
Local file `settings.json`:
{"api_url":"https://example.invalid","token":"do-not-print","region":"test"}

Command:
`python3.12 check_config.py settings.json --required token api_url region signing_key`
```

## Expected output

```text
missing keys: signing_key

The configured values, including `token`, are not printed.
```

## Recorded validation scope

Executed 6 synthetic local fixture cases in isolated CPython 3.12.15 on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/argparse.html
- https://docs.python.org/3.12/library/json.html
