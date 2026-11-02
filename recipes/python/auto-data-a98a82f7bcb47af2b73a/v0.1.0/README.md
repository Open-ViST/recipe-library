# Calculate signed event balances by group with Python – OpenViST

Reconcile signed adjustments into per-group counts and integer balances.

Published recipe: [auto-data-a98a82f7bcb47af2b73a](https://openvist.com/recipes/auto-data-a98a82f7bcb47af2b73a/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.py`

python3 recipe.py < records.json

## Requirements

- Run with Python 3.12 and no CLI arguments. Supply the JSON array through standard input.
- Uses only sys, json and re. Performs no file access, networking, subprocess execution or dynamic execution.
- Validates every record before aggregation, including weight and tag even though they do not affect group totals.
- Implements only group_totals, without filters. Counts records and sums signed values per group, sorting groups in ascending order.
- On success, writes exactly one JSON object to stdout and exits 0 without stderr. Empty input arrays produce {"groups":[]}.
- On input-validation or input-read failure, writes no stdout, emits one short error: line to stderr, and exits 2.

## Steps

- Save the tested code as recipe.py.
- Prepare records.json using the exact input schema below.
- Run python3 recipe.py < records.json.
- Check exit status before consuming the JSON result; exit 2 indicates rejected input.

## Checks

- Initial examples are compared with a trusted reference result.
- Additional tests cover input boundaries, invalid encodings and generated record sets. Consult the bound test reports for actual results.

## Limits

- Reads at most 65537 bytes and rejects input exceeding 65536 bytes.
- Accepts only strict UTF-8 JSON without a leading BOM, duplicate keys, non-finite numbers or trailing non-whitespace.
- Accepts at most 40 records, each containing exactly group, value, weight and tag.
- Group and tag must match [a-z][a-z0-9_-]{0,19}. Value must be an integer from -1000000 through 1000000; weight must be an integer from -1000 through 1000. Booleans and floats are rejected.
- Diagnostics are intentionally generic. Output-write failures are outside the input-error guarantee.
- All validated input is held in memory; 65536 input bytes and 40 records maximum.
- The stdin byte limit is not a deadline; reading can wait for EOF. Output write failures are outside the input error contract.
- Only the documented record schema and this exact workflow are supported; no external data, authentication or integration is provided.

## Example input

```text
[{"group":"beta","value":5,"weight":2,"tag":"keep"},{"group":"alpha","value":-3,"weight":4,"tag":"ignore"},{"group":"beta","value":5,"weight":2,"tag":"keep"},{"group":"alpha","value":0,"weight":0,"tag":"zero"},{"group":"beta","value":2,"weight":-1,"tag":"other"},{"group":"alpha","value":8,"weight":1,"tag":"keep"}]
```

## Expected output

```text
{"groups": [{"group": "alpha", "count": 3, "total": 5}, {"group": "beta", "count": 3, "total": 12}]}
```

## Recorded validation scope

Six primary fixtures and 21 supplementary checks in the configured pinned offline Python image. The publication gate requires their passing reports for the exact code, input plan and documentation. These checks do not prove exhaustive correctness or general usefulness.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/json.html
- https://docs.python.org/3.12/library/sys.html
