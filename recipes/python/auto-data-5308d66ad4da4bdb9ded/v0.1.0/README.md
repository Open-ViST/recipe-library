# Measure event value ranges for each group after positive values with Python – OpenViST

Keep records whose value is strictly greater than zero. Then find minimum, maximum and spread of integer measurements per group.

Published recipe: [auto-data-5308d66ad4da4bdb9ded](https://openvist.com/recipes/auto-data-5308d66ad4da4bdb9ded/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.py`

python3 recipe.py < records.json

## Requirements

- Run with Python 3.12, passing no CLI arguments. Supply one JSON array on standard input.
- Uses only sys, json and re. Performs no file access, networking, process creation or dynamic execution.
- Validates every record before filtering. Rejects duplicate keys at every depth, floats, booleans in integer fields, non-finite values, invalid UTF-8, a leading BOM, malformed JSON and trailing non-whitespace.
- Keeps only records with value strictly greater than zero, then emits only group_extrema: a groups array sorted by group, with group, minimum, maximum and spread fields.
- Success exits 0 with one JSON object on stdout and no stderr. Input-validation or input-read failures exit 2 with no stdout and one short error: line on stderr.

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
- Accepts 0 to 40 records, each containing exactly group, value, weight and tag.
- Group and tag must match [a-z][a-z0-9_-]{0,19}. Value must be an integer from -1000000 through 1000000; weight must be an integer from -1000 through 1000.
- Empty input arrays and inputs with no surviving records produce {"groups":[]}. Weight and tag are validated but do not affect extrema.
- No other terminal operations or filters are implemented. Output write failures are outside the error-handling guarantee.
- All validated input is held in memory; 65536 input bytes and 40 records maximum.
- The stdin byte limit is not a deadline; reading can wait for EOF. Output write failures are outside the input error contract.
- Only the documented record schema and this exact workflow are supported; no external data, authentication or integration is provided.

## Example input

```text
[{"group":"beta","value":5,"weight":2,"tag":"keep"},{"group":"alpha","value":-3,"weight":4,"tag":"ignore"},{"group":"beta","value":5,"weight":2,"tag":"keep"},{"group":"alpha","value":0,"weight":0,"tag":"zero"},{"group":"beta","value":2,"weight":-1,"tag":"other"},{"group":"alpha","value":8,"weight":1,"tag":"keep"}]
```

## Expected output

```text
{"groups": [{"group": "alpha", "minimum": 8, "maximum": 8, "spread": 0}, {"group": "beta", "minimum": 2, "maximum": 5, "spread": 3}]}
```

## Recorded validation scope

Six primary fixtures and 21 supplementary checks in the configured pinned offline Python image. The publication gate requires their passing reports for the exact code, input plan and documentation. These checks do not prove exhaustive correctness or general usefulness.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/json.html
- https://docs.python.org/3.12/library/sys.html
