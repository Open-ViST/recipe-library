# Validate and summarize recent filings in a saved SEC submissions JSON

Read a saved SEC submissions JSON file, validate the parallel recent-filing arrays for form, filing date, accession number and primary document, then print aligned records or a clear validation error.

Published recipe: [validate-saved-sec-submissions-recent-filings](https://openvist.com/recipes/validate-saved-sec-submissions-recent-filings/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `sec_recent.py`

Run with Python 3.12: `python3.12 sec_recent.py saved-submissions.json`. To read from stdin, use `python3.12 sec_recent.py - < saved-submissions.json`.

## Requirements

- Intended runner: Python 3.12; no third-party packages or network access are required. This is not a claim of a tested minimum Python version.
- Provide a local UTF-8 JSON file or pipe JSON to stdin using `-`; the input must represent an SEC submissions object with `filings.recent`.
- For non-empty records, each selected array entry must be a string. The code does not validate date formats, accession-number formats, or document names beyond that type check.

## Steps

- Save the proposed code as `sec_recent.py`.
- Create a small synthetic JSON fixture using the four arrays shown in `example_input`.
- Run the fixture with `python3.12 sec_recent.py fixture.json` and check that each output row keeps the fields from the same array index together.
- Run the same fixture through stdin with `python3.12 sec_recent.py - < fixture.json` and compare the output.
- Change one array to a different length and confirm the program rejects it rather than pairing incomplete rows.
- Set all four arrays to empty lists and confirm it prints the explicit empty-record message.

## Checks

- Use a normal synthetic fixture with two rows; verify the four displayed fields remain aligned by index and the count is two.
- Use a fixture whose four arrays are all empty; verify `No recent filing records.` is printed.
- Use a fixture with unequal array lengths; verify an error identifies the observed lengths and no filing summary is printed.
- Use malformed JSON and a top-level JSON array; verify each is rejected with an actionable error.
- Use a fixture with a missing array and another with a non-string record field; verify both are rejected.
- Pass a nonexistent path; verify a read error is reported and the process exits nonzero.

## Limits

- Only summarizes `filings.recent`; it does not read older filing-history files mentioned by SEC documentation.
- This offline processor does not establish whether a saved response is current, complete, authentic, or actually retrieved from the SEC.
- The recipe rejects unequal array lengths and non-string values in records, but does not impose additional SEC schema rules.
- A missing file, unreadable file, malformed JSON, missing object path, missing array, or invalid record produces an error on stderr and exit status 2.
- There are no network calls, so no timeout or retry behavior applies.
- The Python JSON documentation cautions that parsing untrusted, very large JSON can consume significant CPU and memory; use appropriately bounded local input.

## Example input

```text
{"filings":{"recent":{"form":["10-K","8-K"],"filingDate":["2025-02-20","2025-03-01"],"accessionNumber":["0000000000-25-000001","0000000000-25-000002"],"primaryDocument":["annual.htm","event.htm"]}}}
```

## Expected output

```text
Recent filing records: 2
1. 10-K | 2025-02-20 | 0000000000-25-000001 | annual.htm
2. 8-K | 2025-03-01 | 0000000000-25-000002 | event.htm
```

## Recorded validation scope

Executed 6 synthetic local fixture cases in isolated CPython 3.12.15 on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- https://docs.python.org/3.12/library/json.html
