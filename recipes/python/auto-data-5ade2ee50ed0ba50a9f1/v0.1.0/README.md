# Calculate weighted event totals by group after positive values with Python – OpenViST

Keep records whose value is strictly greater than zero. Then multiply each signed value by its weight, then sum the products per group.

Published recipe: [auto-data-5ade2ee50ed0ba50a9f1](https://openvist.com/recipes/auto-data-5ade2ee50ed0ba50a9f1/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.py`

python3 recipe.py < records.json

## Requirements

- Run with Python 3.12 and no CLI arguments. Supply the JSON array through standard input; read the single JSON result from standard output.
- Uses only sys, json, and re. Performs no file access, networking, process creation, or dynamic execution.
- Validates every record before filtering. Retains only records with value > 0, then sums value * weight per group.
- Outputs only {"groups":[{"group":...,"weighted_total":...}]}, sorted by group ascending. Groups with surviving records remain present even when their total is zero.
- Success exits 0 without stderr. Validation or input-read errors exit 2 with no stdout and one short error line on stderr.

## Steps

- Save the tested code as recipe.py.
- Prepare records.json using the exact input schema below.
- Run python3 recipe.py < records.json.
- Check exit status before consuming the JSON result; exit 2 indicates rejected input.

## Checks

- Initial examples are compared with a trusted reference result.
- Additional tests cover input boundaries, invalid encodings and generated record sets. Consult the bound test reports for actual results.

## Limits

- Reads at most 65537 bytes and rejects inputs longer than 65536 bytes.
- Requires strict UTF-8 without a leading BOM and one complete JSON document. Rejects duplicate keys at every depth, floats, non-finite constants, and trailing non-whitespace.
- Accepts 0–40 records, each containing exactly group, value, weight, and tag. Names must match [a-z][a-z0-9_-]{0,19}; integer ranges are enforced and booleans are rejected.
- Implements only positive_values followed by weighted_totals. Empty input or no surviving records produces {"groups":[]}.
- Output-write failures are outside the error-handling guarantee.
- All validated input is held in memory; 65536 input bytes and 40 records maximum.
- The stdin byte limit is not a deadline; reading can wait for EOF. Output write failures are outside the input error contract.
- Only the documented record schema and this exact workflow are supported; no external data, authentication or integration is provided.

## Example input

```text
[{"group":"beta","value":5,"weight":2,"tag":"keep"},{"group":"alpha","value":-3,"weight":4,"tag":"ignore"},{"group":"beta","value":5,"weight":2,"tag":"keep"},{"group":"alpha","value":0,"weight":0,"tag":"zero"},{"group":"beta","value":2,"weight":-1,"tag":"other"},{"group":"alpha","value":8,"weight":1,"tag":"keep"}]
```

## Expected output

```text
{"groups": [{"group": "alpha", "weighted_total": 8}, {"group": "beta", "weighted_total": 18}]}
```

## Recorded validation scope

Six primary fixtures and 21 supplementary checks in the configured pinned offline Python image. The publication gate requires their passing reports for the exact code, input plan and documentation. These checks do not prove exhaustive correctness or general usefulness.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/json.html
- https://docs.python.org/3.12/library/sys.html
