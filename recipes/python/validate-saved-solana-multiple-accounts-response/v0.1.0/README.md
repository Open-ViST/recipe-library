# Validate owners and lamports in a saved Solana getMultipleAccounts response

Read a saved Solana getMultipleAccounts JSON-RPC response, preserve each value’s request-order index, identify null accounts, and validate the owner and non-negative integer lamports of every present account.

Published recipe: [validate-saved-solana-multiple-accounts-response](https://openvist.com/recipes/validate-saved-solana-multiple-accounts-response/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `check_accounts.py`

Save the script as check_accounts.py, then run `python3.12 check_accounts.py saved-response.json`. To supply the saved response on stdin, run `python3.12 check_accounts.py - < saved-response.json`. The program performs no network requests, retries, or writes to files; it reads the chosen local input and writes its report to stdout.

## Requirements

- Intended runner: Python 3.12; no third-party packages or installation are required.
- Input must be a saved JSON response shaped like a JSON-RPC object with a result object containing a value array, or the same JSON supplied through stdin using the - argument.
- Owner validation checks only that owner is a non-empty string; lamports validation requires a non-negative Python integer and rejects booleans. It does not validate public-key syntax, decode account data, or verify the response against a request.

## Steps

- Save the code as check_accounts.py using Python 3.12.
- Save a getMultipleAccounts response as a local JSON file, or prepare it for stdin.
- Run the script with the file path or `-` to read stdin.
- Review the printed indices against the response value-array order; a null entry is reported rather than treated as a missing index.
- If the process exits nonzero, inspect stderr for input or response-shape errors, or the report for invalid account fields.

## Checks

- Run the synthetic example and confirm it prints indices 0, 1, and 2 in order, with index 1 marked null.
- Try an empty value array and confirm the report is an empty JSON array.
- Try malformed JSON and confirm an invalid-JSON diagnostic goes to stderr with a nonzero exit status.
- Try a missing file and confirm a read error goes to stderr with a nonzero exit status.
- Try a present account with a missing or empty owner, a negative lamports value, a floating-point lamports value, and a boolean lamports value; confirm each is marked invalid and the process exits nonzero.
- Try a top-level array, absent result.value, or a response containing an error field; confirm each is rejected rather than reported as an account list.

## Limits

- The zero-based index identifies an entry in result.value; the response alone may not provide the original requested public keys.
- This checks only response structure, owner string presence, and lamports type/range; it does not validate account data or establish that a response came from Solana.
- A syntactically valid JSON document can still be large or consume substantial parsing resources; use an appropriately bounded trusted local fixture.
- No timeout is needed because the script performs no network calls.

## Example input

```text
{"jsonrpc":"2.0","id":1,"result":{"context":{"slot":341197247},"value":[{"owner":"11111111111111111111111111111111","lamports":42,"data":["","base64"]},null,{"owner":"ExampleOwner","lamports":0}]}}
```

## Expected output

```text
[
  {
    "index": 0,
    "status": "valid",
    "owner": "11111111111111111111111111111111",
    "lamports": 42
  },
  {
    "index": 1,
    "status": "null"
  },
  {
    "index": 2,
    "status": "valid",
    "owner": "ExampleOwner",
    "lamports": 0
  }
]
```

## Recorded validation scope

Executed 6 synthetic local fixture cases in isolated CPython 3.12.15 on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://solana.com/docs/rpc/http/getmultipleaccounts
- https://docs.python.org/3.12/library/json.html
