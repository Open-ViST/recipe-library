# Track running balances within interleaved event groups with Python – OpenViST

Preserve event order while maintaining an independent running balance for each group.

Published recipe: [auto-data-4ddb24cd3f8435dac51c](https://openvist.com/recipes/auto-data-4ddb24cd3f8435dac51c/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.py`

python3 recipe.py < records.json

## Requirements

- Run with Python 3.12, for example: python3.12 running_totals.py. Supply the JSON array on standard input; pass no CLI arguments.
- Uses only sys, json and re. Performs no file access, networking, process creation or dynamic execution.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8 without a leading BOM and one complete JSON value without trailing non-whitespace.
- Rejects duplicate object keys at every depth, non-finite numbers, floats, invalid record fields, invalid string identifiers, booleans in integer fields and out-of-range integers.
- Validates every record before calculating balances. Applies no filters and preserves input order, maintaining an independent sum of value for each group.
- Outputs exactly one object containing records, each retaining all original fields plus running_total. Empty input produces {"records":[]}.
- Success exits 0 with no stderr. Input-validation or input-read failures exit 2 with no stdout and one bounded error line on stderr.

## Steps

- Save the tested code as recipe.py.
- Prepare records.json using the exact input schema below.
- Run python3 recipe.py < records.json.
- Check exit status before consuming the JSON result; exit 2 indicates rejected input.

## Checks

- Initial examples are compared with a trusted reference result.
- Additional tests cover input boundaries, invalid encodings and generated record sets. Consult the bound test reports for actual results.

## Limits

- Input must contain 0–40 records, each with exactly group, value, weight and tag.
- Group and tag must match [a-z][a-z0-9_-]{0,19}. Value must be an integer from -1000000 through 1000000; weight must be an integer from -1000 through 1000.
- Only running_totals is implemented. Weight and tag are validated and preserved but do not affect balances.
- Errors use a generic diagnostic. Output-write failures are outside the error-handling guarantee.
- All validated input is held in memory; 65536 input bytes and 40 records maximum.
- The stdin byte limit is not a deadline; reading can wait for EOF. Output write failures are outside the input error contract.
- Only the documented record schema and this exact workflow are supported; no external data, authentication or integration is provided.

## Example input

```text
[{"group":"beta","value":5,"weight":2,"tag":"keep"},{"group":"alpha","value":-3,"weight":4,"tag":"ignore"},{"group":"beta","value":5,"weight":2,"tag":"keep"},{"group":"alpha","value":0,"weight":0,"tag":"zero"},{"group":"beta","value":2,"weight":-1,"tag":"other"},{"group":"alpha","value":8,"weight":1,"tag":"keep"}]
```

## Expected output

```text
{"records": [{"group": "beta", "value": 5, "weight": 2, "tag": "keep", "running_total": 5}, {"group": "alpha", "value": -3, "weight": 4, "tag": "ignore", "running_total": -3}, {"group": "beta", "value": 5, "weight": 2, "tag": "keep", "running_total": 10}, {"group": "alpha", "value": 0, "weight": 0, "tag": "zero", "running_total": -3}, {"group": "beta", "value": 2, "weight": -1, "tag": "other", "running_total": 12}, {"group": "alpha", "value": 8, "weight": 1, "tag": "keep", "running_total": 5}]}
```

## Recorded validation scope

Six primary fixtures and 21 supplementary checks in the configured pinned offline Python image. The publication gate requires their passing reports for the exact code, input plan and documentation. These checks do not prove exhaustive correctness or general usefulness.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/json.html
- https://docs.python.org/3.12/library/sys.html
