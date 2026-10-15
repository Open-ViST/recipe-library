# Calculate effective PumpSwap quote reserves from pool values

Given a PumpSwap pool's quote-vault token amount and signed virtual quote reserves, calculate and display the effective quote reserves used for quoting and pricing.

Published recipe: [pump-read-effective-pool-reserves](https://openvist.com/recipes/pump-read-effective-pool-reserves/)

**Language:** python · **Version:** 0.1.1 · **License:** MIT

## Usage

Code file: `recipe.py`

Save as recipe.py. Run python3 recipe.py 1000000 -125000. Both arguments must be integers in the same smallest-unit denomination. Local calculation only; no network or transactions.

## Requirements

- Python 3.12 is the independently tested runtime (CPython 3.12.15); standard library only. The code uses f-strings. Older Python versions have not been tested for this Recipe.
- Input: a non-negative quote-vault integer and a signed virtual-reserve integer, both in the same smallest-unit denomination. No endpoint, network, credentials, SDK, or API version is needed.
- The official PumpSwap documentation specifies the formula and says the virtual reserve field is signed i128; it guarantees the sum will not overflow or be negative for valid pool data.

## Steps

- Supply the quote-vault amount and signed virtual quote reserves as the two CLI arguments; both must use the same token denomination.
- Run python3 recipe.py 1000000 -125000; expect Effective quote reserves: 875000. Invalid arguments or negative amounts/results exit 2.
- Read the printed effective reserve total. The negative virtual reserve in the sample demonstrates why adding a signed value matters.
- Use the total as effective quote reserves if implementing a separate quote calculation; this example does not calculate a trade price or execute a trade.

## Checks

- Run with 1000000 -125000: expect Effective quote reserves: 875000 and exit 0.
- Run with 10 0 and 10 -10: expect 10 and 0, respectively.
- Run with 10 -11 and -1 0: expect exit 2 and Invalid pool values on stderr.
- Run with abc 0 or True 0: expect argparse exit 2. Missing or extra arguments must also fail.

## Limits

- The supplied source excerpt establishes the PumpSwap formula but does not establish an API endpoint, account-fetching method, or particular SDK. Accordingly the example accepts manually supplied values and makes no claims about retrieving live pool state.
- The example does not establish pool authenticity or validate that numbers were decoded from the correct on-chain fields; obtain and decode pool data using separately verified documentation before relying on a result.
- No HTTP call is made, so timeout, API credential, and remote failure handling are not applicable. Input type and non-negative-result failures are handled explicitly; there are no retries.
- Provenance: recorded as an original, AI-assisted OpenViST example with an MIT declaration for this example only. Pump.fun documentation supports the formula and field semantics, not the authorship or license of this example. This is not an official Pump.fun SDK.
- Six synthetic CLI cases were independently executed. Boolean function arguments, missing/extra CLI arguments and fixed-width overflow boundaries are not fixture-verified. Python integers do not enforce signed i128 limits.

## Recorded validation scope

Executed 6 synthetic local fixture cases in isolated CPython 3.12.15 on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://github.com/pump-fun/pump-public-docs
- https://pump.fun/
