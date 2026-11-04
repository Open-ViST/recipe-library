# Track running balances within interleaved event groups after positive values with Python – OpenViST

Keep records whose value is strictly greater than zero. Then preserve event order while maintaining an independent running balance for each group.

Published recipe: [auto-data-e8fe6621ae6783c3ed40](https://openvist.com/recipes/auto-data-e8fe6621ae6783c3ed40/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.py`

python3 recipe.py < records.json

## Requirements

- Run with Python 3.12 and no CLI arguments. Supply one JSON array on standard input.
- Uses only sys, json and re. Performs no file access, networking, process creation or dynamic execution.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8 without a leading BOM and rejects malformed JSON, duplicate keys at every depth, non-finite numbers and trailing non-whitespace.
- Validates every record before filtering: at most 40 objects, exactly group/value/weight/tag, matching ASCII identifiers, and integers within the specified bounds. Booleans and floats are rejected.
- Keeps only records with value greater than zero, preserves their input order and adds running_total using an independent sum of surviving values for each group.
- Outputs exactly one JSON object with a records array. Success exits 0 without stderr. Input-validation or input-read errors exit 2 with no stdout and one short error line on stderr.

## Steps

- Save the tested code as recipe.py.
- Prepare records.json using the exact input schema below.
- Run python3 recipe.py < records.json.
- Check exit status before consuming the JSON result; exit 2 indicates rejected input.

## Checks

- Initial examples are compared with a trusted reference result.
- Additional tests cover input boundaries, invalid encodings and generated record sets. Consult the bound test reports for actual results.

## Limits

- Only positive_values followed by running_totals is implemented; other terminal operations are not supported.
- Weight and tag are validated and preserved but do not affect running totals.
- Output write failures are outside the error-output guarantee.
- All validated input is held in memory; 65536 input bytes and 40 records maximum.
- The stdin byte limit is not a deadline; reading can wait for EOF. Output write failures are outside the input error contract.
- Only the documented record schema and this exact workflow are supported; no external data, authentication or integration is provided.

## Example input

```text
[{"group":"beta","value":5,"weight":2,"tag":"keep"},{"group":"alpha","value":-3,"weight":4,"tag":"ignore"},{"group":"beta","value":5,"weight":2,"tag":"keep"},{"group":"alpha","value":0,"weight":0,"tag":"zero"},{"group":"beta","value":2,"weight":-1,"tag":"other"},{"group":"alpha","value":8,"weight":1,"tag":"keep"}]
```

## Expected output

```text
{"records": [{"group": "beta", "value": 5, "weight": 2, "tag": "keep", "running_total": 5}, {"group": "beta", "value": 5, "weight": 2, "tag": "keep", "running_total": 10}, {"group": "beta", "value": 2, "weight": -1, "tag": "other", "running_total": 12}, {"group": "alpha", "value": 8, "weight": 1, "tag": "keep", "running_total": 8}]}
```

## Recorded validation scope

Six primary fixtures and 21 supplementary checks in the configured pinned offline Python image. The publication gate requires their passing reports for the exact code, input plan and documentation. These checks do not prove exhaustive correctness or general usefulness.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/json.html
- https://docs.python.org/3.12/library/sys.html
