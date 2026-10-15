# Read a saved CoinGecko price for an explicit asset and currency

Read a saved CoinGecko `/simple/price` JSON response, select one asset ID and quote currency from CLI arguments, and print its finite numeric price while making clear it is not a current quote.

Published recipe: [read-saved-coingecko-simple-price](https://openvist.com/recipes/read-saved-coingecko-simple-price/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `saved_price.py`

Save the code as `saved_price.py`, then run `python3.12 saved_price.py response.json bitcoin usd`. Use `-` instead of the file path to read JSON from stdin, for example `cat response.json | python3.12 saved_price.py - bitcoin usd`.

## Requirements

- Intended runner: Python 3.12; no third-party packages or installation are required.
- Provide a saved JSON object matching the documented simple-price response shape, either as a local file or on stdin.
- Supply one explicit asset ID and one quote-currency key as positional CLI arguments.
- No credentials, live API access, or external service calls are used.

## Steps

- Save the code as `saved_price.py`.
- Save a simple-price JSON response locally, or prepare the same JSON text for stdin.
- Run the script with the input path, explicit asset ID, and quote currency; use `-` as the path for stdin.
- Confirm the printed value is labeled as a saved observation, not a current quote.
- Try invalid or missing input cases and check that errors go to stderr with a nonzero exit status.

## Checks

- Normal case: provide `{"bitcoin":{"usd":76975}}` and run with `bitcoin usd`; verify the two expected output lines.
- Selection checks: try an unknown asset ID, an asset value that is not an object, and a missing currency key; each should produce a clear stderr error and nonzero exit.
- Value checks: try null, a string, a boolean, and a JSON non-finite constant such as `NaN`; each must be rejected.
- Malformed/empty checks: try an empty file and malformed JSON; both should fail without printing a price.
- Missing-file check: pass a nonexistent path and verify the read error is reported to stderr with nonzero exit.
- Stdin check: pipe a valid synthetic JSON object into the command with `-` and verify it selects the requested pair.

## Limits

- Only reads the selected field from saved JSON; it does not fetch data, verify timestamps, or assess freshness.
- The source docs establish the response shape and numeric price field, but do not specify a minimum supported Python version; Python 3.12 is the intended runner.
- Input is read entirely into memory; use only appropriately sized local fixtures.

## Example input

```text
{"bitcoin":{"usd":76975,"last_updated_at":1779092258},"ethereum":{"usd":2450}}
```

## Expected output

```text
Saved observation: bitcoin/usd = 76975
This is a saved observation, not a current quote.
```

## Recorded validation scope

Executed 6 synthetic local fixture cases in isolated CPython 3.12.15 on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.coingecko.com/reference/simple-price
- https://docs.python.org/3.12/library/json.html
