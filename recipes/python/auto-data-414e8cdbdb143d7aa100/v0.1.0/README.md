# Select each group’s highest-value event with Python – OpenViST

Choose the first highest-value record in each group, preserving the complete selected record.

Published recipe: [auto-data-414e8cdbdb143d7aa100](https://openvist.com/recipes/auto-data-414e8cdbdb143d7aa100/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.py`

python3 recipe.py < records.json

## Requirements

- Save the code as a Python script and run it with Python 3.12, without CLI arguments. Supply the JSON array through standard input.
- Uses only sys, json and re. Reads at most 65537 bytes and rejects input exceeding 65536 bytes.
- Validates strict UTF-8, JSON syntax, duplicate keys at every depth, exact record fields, string patterns and integer ranges before selecting records.
- Applies no filters. Selects the first highest-value complete record per group and sorts the selected records by group.
- Success emits exactly one JSON object with a groups array and exits 0 without stderr. Input-validation or input-read errors emit no stdout, write one short error: line to stderr and exit 2.

## Steps

- Save the tested code as recipe.py.
- Prepare records.json using the exact input schema below.
- Run python3 recipe.py < records.json.
- Check exit status before consuming the JSON result; exit 2 indicates rejected input.

## Checks

- Initial examples are compared with a trusted reference result.
- Additional tests cover input boundaries, invalid encodings and generated record sets. Consult the bound test reports for actual results.

## Limits

- Accepts at most 40 records. Empty input arrays produce {"groups":[]}.
- Only top_per_group is implemented; other aggregation and ranking operations are not supported.
- No file access, network access, process creation or dynamic execution is used.
- Output write failures are outside the error-handling guarantee.
- All validated input is held in memory; 65536 input bytes and 40 records maximum.
- The stdin byte limit is not a deadline; reading can wait for EOF. Output write failures are outside the input error contract.
- Only the documented record schema and this exact workflow are supported; no external data, authentication or integration is provided.

## Example input

```text
[{"group":"beta","value":5,"weight":2,"tag":"keep"},{"group":"alpha","value":-3,"weight":4,"tag":"ignore"},{"group":"beta","value":5,"weight":2,"tag":"keep"},{"group":"alpha","value":0,"weight":0,"tag":"zero"},{"group":"beta","value":2,"weight":-1,"tag":"other"},{"group":"alpha","value":8,"weight":1,"tag":"keep"}]
```

## Expected output

```text
{"groups": [{"group": "alpha", "value": 8, "weight": 1, "tag": "keep"}, {"group": "beta", "value": 5, "weight": 2, "tag": "keep"}]}
```

## Recorded validation scope

Six primary fixtures and 21 supplementary checks in the configured pinned offline Python image. The publication gate requires their passing reports for the exact code, input plan and documentation. These checks do not prove exhaustive correctness or general usefulness.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/json.html
- https://docs.python.org/3.12/library/sys.html
