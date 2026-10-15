# Group HTTP(S) URLs by Hostname from a Local Text File

Read a UTF-8 text file or standard input, parse each nonempty line as an absolute HTTP(S) URL, and print a JSON object of hostname counts. Reject malformed lines without fetching any URL.

Published recipe: [summarize-http-urls-by-hostname](https://openvist.com/recipes/summarize-http-urls-by-hostname/)

**Language:** javascript · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `url-host-summary.js`

Save the code as `url-host-summary.js`. Run `node url-host-summary.js urls.txt` to read a UTF-8 file, or `node url-host-summary.js - < urls.txt` to read stdin. The program prints JSON to stdout; input and validation failures are written to stderr and exit nonzero. Intended runner: Node.js 22.

## Requirements

- Node.js 22; no external packages are used.
- A UTF-8 newline-delimited text file, or a stream piped to stdin.
- Each nonblank line must contain one absolute HTTP or HTTPS URL. Leading and trailing whitespace on a line is ignored.

## Steps

- Save the CommonJS code to `url-host-summary.js`.
- Put one absolute HTTP(S) URL on each line of a text file, or prepare input on stdin.
- Run `node url-host-summary.js <file-path>` or `node url-host-summary.js - < <file-path>`.
- Inspect the hostname-count JSON on stdout. Correct any rejected lines using the line numbers reported on stderr, then run again.

## Checks

- Run the supplied example and confirm its output matches `expected_output`.
- Try a file containing the same hostname with different casing and ports; confirm it produces one hostname key with the combined count.
- Try `mailto:sample` or malformed URL text on a line; confirm the command reports its one-based line number to stderr and exits nonzero.
- Run with `-` and pipe the same fixture through stdin; confirm the result matches file input.
- Review the script to confirm it contains no networking or filesystem-write operations.

## Limits

- Blank lines are ignored; comments and other nonblank text are treated as URLs and rejected if invalid.
- The WHATWG URL parser defines normalization, including lowercasing hostnames and internationalized-domain handling. Counts do not include ports or distinguish HTTP from HTTPS.
- This reads the entire input into memory and is intended for reasonably sized local text files.
- If any nonblank line is invalid or uses a non-HTTP(S) scheme, the command reports errors and produces no count output.
- The file contents are treated only as data. The program does not fetch, resolve, or otherwise contact any URL.

## Example input

```text
https://example.com/docs
http://example.com:8080/status
https://api.example.net/v1

```

## Expected output

```text
{
  "api.example.net": 1,
  "example.com": 2
}

```

## Recorded validation scope

Executed 5 synthetic local fixture cases in isolated Node.js 22.23.3 on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://nodejs.org/docs/latest-v22.x/api/url.html
- https://nodejs.org/docs/latest-v22.x/api/process.html
