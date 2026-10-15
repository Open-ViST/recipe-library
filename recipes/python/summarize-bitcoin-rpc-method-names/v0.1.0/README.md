# List Bitcoin Core RPC method names from saved reference text

Read a user-supplied local copy of the Bitcoin developer reference and print the distinct RPC method names explicitly named in its RPC API Reference section.

Published recipe: [summarize-bitcoin-rpc-method-names](https://openvist.com/recipes/summarize-bitcoin-rpc-method-names/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.py`

See requirements below.

## Requirements

- Python 3.12 was used for the recorded GitHub Actions fixture tests. The example uses only the Python standard library; compatibility with other Python versions was not established by those tests.
- A local UTF-8 text fixture with the exact markers `RPC API Reference` and `Network Status`, and method entries directly before `Argument #` or `Result`. These are parser input requirements, not a guaranteed export format of the linked websites. No Bitcoin node, credentials, packages, or network access are needed.

## Steps

- Prepare a local UTF-8 fixture using method names documented in the official RPC reference. Include the exact section markers and entry format described below; an arbitrary saved web page is not guaranteed to match this parser.
- Save the example as `list_rpc_names.py`.
- Run `python list_rpc_names.py reference.txt`, replacing the argument with the path to the saved text.
- Review the printed, alphabetically sorted, distinct method names; they are extracted from this file only, not verified against a running service.

## Checks

- Use a synthetic text fixture containing both section markers and entries such as `getblock Argument #1` and `getdifficulty Result`; check that each distinct extracted name prints once, in alphabetical order.
- Try a fixture with the section markers but no matching method entries; confirm the program reports the no-methods error to stderr and exits with status 2.
- Try an empty file and a nonexistent path; confirm each reports an error and exits with status 2.
- Remove either required section marker from a nonempty fixture; confirm the corresponding missing-marker or missing-boundary error appears, with no partial output.
- Check that stdout contains only extracted names and that no remote service is contacted or modified.

## Limits

- This is a bounded offline text extraction, not an RPC client or a test of Bitcoin Core.
- The parser requires the two exact section markers in a prepared local fixture. It has not been validated against an unmodified text export of the current reference website.
- Names are inferred from text immediately preceding `Argument #` or `Result`; unusual formatting or unrelated matching text can affect results.
- The recipe does not interpret method arguments, return values, or version availability. The supplied documents do not establish an exact Bitcoin Core version requirement.

## Recorded validation scope

Executed 6 synthetic local fixture cases in isolated CPython on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://developer.bitcoin.org/
- https://bitcoin.org/
