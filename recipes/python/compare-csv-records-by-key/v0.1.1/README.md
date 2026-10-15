# Compare Local CSV Records by a Chosen Key

Compare two local CSV files using a CLI-selected key column and report keys that are added, removed, or present in both files with changed values, without modifying either file.

Published recipe: [compare-csv-records-by-key](https://openvist.com/recipes/compare-csv-records-by-key/)

**Language:** python · **Version:** 0.1.1 · **License:** MIT

## Usage

Code file: `compare_csv_records.py`

Save the code as `compare_csv_records.py`, then run `python3 compare_csv_records.py before.csv after.csv --key id`. Use `-h` for the CLI help. The intended runner is Python 3.12; no tested minimum version is claimed.

## Requirements

- Python 3.12 is the intended runner; this is not a claim of a tested minimum version.
- Uses only Python standard-library `argparse`, `csv`, `json`, `pathlib`, and `sys`.
- Requires two readable UTF-8 CSV files with headers and a key column named by `--key`.
- Each file must have unique, nonblank key values and consistent row widths.
- Both snapshots must have the same column names; column order may differ. Different schemas are rejected with exit 2.

## Steps

- Pass the earlier and later CSV paths as positional CLI arguments and supply the exact key header with `--key`.
- Open each file as UTF-8 with `newline=''` so the CSV reader handles newline conventions and quoted fields.
- Reject missing headers, duplicate header names, a missing key column, malformed CSV, inconsistent row widths, blank keys, and duplicate keys; report errors on stderr and return a nonzero status.
- Store records by key and compare shared records field by field, excluding the key column from change detection.
- Sort the reported keys and changed field names for stable output, then write one JSON object to stdout; do not print cell values for changed fields.

## Checks

- Run the shown example and confirm the JSON reports `r3` as added, `r2` as removed, and `status` as changed for `r1`.
- Try two header-only files with the same key header and confirm the output contains empty `added`, `removed`, and `changed` arrays.
- Try a CSV with a duplicate key, a blank key, a row with too few fields, and a row with too many fields; confirm each is rejected with an error on stderr and no JSON result on stdout.
- Try a missing input path and a file containing invalid UTF-8; confirm both fail clearly without a traceback being presented as a successful comparison.
- Try a quoted field containing a comma and confirm it is read as one field; verify identical records produce no `changed` entry.
- Try different header sets with a shared key and a shared record: expect exit 2 and no traceback. Try the same columns in a different order: compare successfully. Try malformed quoting: expect exit 2.

## Limits

- Compares only local CSV snapshots and never contacts or tests an external service.
- Requires the chosen key to be unique and nonblank in each file; it does not infer identity or merge duplicate records.
- Treats all CSV fields as strings and compares them exactly, without type conversion, normalization, or whitespace trimming.
- The report identifies changed field names but intentionally omits prior and new field values.
- Independent GitHub Actions testing executed six synthetic local cases in CPython 3.12.15: added/removed/changed records, header-only files, reordered columns, duplicate keys, differing header sets and malformed quoting. The stored receipt verifies these cases only; additional checks below are suggested tests, not claims of execution.
- Blank keys, short/extra rows, missing files and invalid UTF-8 have rejection paths in the implementation but are not covered by the six saved fixtures. Live services, production data, very large files and resource limits are outside tested scope.
- Provenance: stored as an original, AI-assisted OpenViST example with an MIT declaration for this example. Python documentation supports standard-library behavior; it does not establish this example's authorship or licensing. No third-party code license is inferred from those sources.

## Example input

```text
before.csv:
id,name,status
r1,Worker,ready
r2,Watcher,idle

after.csv:
id,name,status
r1,Worker,active
r3,Indexer,ready
```

## Expected output

```text
{"added": ["r3"], "changed": [{"fields": ["status"], "key": "r1"}], "removed": ["r2"]}
```

## Recorded validation scope

Executed 6 synthetic local fixture cases in isolated CPython 3.12.15 on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/csv.html
- https://docs.python.org/3.12/library/argparse.html
