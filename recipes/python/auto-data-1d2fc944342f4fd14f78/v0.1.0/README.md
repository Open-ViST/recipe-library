# Inventory distinct event tags by group with Python – OpenViST

Build sorted inventories of observed tag names within each group.

Published recipe: [auto-data-1d2fc944342f4fd14f78](https://openvist.com/recipes/auto-data-1d2fc944342f4fd14f78/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.py`

python3 recipe.py < records.json

## Requirements

- Run with Python 3.12, no CLI arguments, and supply one JSON array through standard input.
- Uses only sys, json and re. Performs no file, network or process access.
- Reads at most 65537 bytes and rejects input exceeding 65536 bytes. Requires strict UTF-8 without a leading BOM and rejects malformed JSON, duplicate keys at every depth, non-finite numbers and trailing non-whitespace.
- Validates every record before aggregation, including exact fields, ASCII names, integer types and numeric bounds.
- Implements only distinct_tags with no filters: groups and their unique tag inventories are sorted ascending.
- Success emits exactly one JSON object and exits 0 without stderr. Input-validation or input-read errors emit no stdout, write one short error: line to stderr and exit 2.

## Steps

- Save the tested code as recipe.py.
- Prepare records.json using the exact input schema below.
- Run python3 recipe.py < records.json.
- Check exit status before consuming the JSON result; exit 2 indicates rejected input.

## Checks

- Initial examples are compared with a trusted reference result.
- Additional tests cover input boundaries, invalid encodings and generated record sets. Consult the bound test reports for actual results.

## Limits

- Input is limited to 40 records and 65536 UTF-8 bytes.
- Other terminal operations and workflow selection are not implemented.
- Error messages are intentionally generic.
- Output write failures are outside the input-error guarantee.
- All validated input is held in memory; 65536 input bytes and 40 records maximum.
- The stdin byte limit is not a deadline; reading can wait for EOF. Output write failures are outside the input error contract.
- Only the documented record schema and this exact workflow are supported; no external data, authentication or integration is provided.

## Example input

```text
[{"group":"beta","value":5,"weight":2,"tag":"keep"},{"group":"alpha","value":-3,"weight":4,"tag":"ignore"},{"group":"beta","value":5,"weight":2,"tag":"keep"},{"group":"alpha","value":0,"weight":0,"tag":"zero"},{"group":"beta","value":2,"weight":-1,"tag":"other"},{"group":"alpha","value":8,"weight":1,"tag":"keep"}]
```

## Expected output

```text
{"groups": [{"group": "alpha", "tags": ["ignore", "keep", "zero"]}, {"group": "beta", "tags": ["keep", "other"]}]}
```

## Recorded validation scope

Six primary fixtures and 21 supplementary checks in the configured pinned offline Python image. The publication gate requires their passing reports for the exact code, input plan and documentation. These checks do not prove exhaustive correctness or general usefulness.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/json.html
- https://docs.python.org/3.12/library/sys.html
