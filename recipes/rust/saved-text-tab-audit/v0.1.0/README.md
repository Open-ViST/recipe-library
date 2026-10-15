# Audit Tabs in Saved Text

Read one UTF-8 text file or standard input and report the total number of tab characters, the number of lines containing at least one tab, and the one-based line numbers of those lines. Treat the input as read-only data; do not execute or modify it.

Published recipe: [saved-text-tab-audit](https://openvist.com/recipes/saved-text-tab-audit/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

Intended runner: Rust 1.90.0, edition 2021. Save the code as `recipe.rs`, then compile with `rustc --edition=2021 recipe.rs -o recipe`. Run `./recipe <file-path>` or use `./recipe -` to read standard input. Exactly one argument is required. A file is only opened for reading. Actionable usage, I/O, and UTF-8 errors are printed to stderr with a nonzero exit status.

## Requirements

- Use only the Rust standard library; no external crates, unsafe code, include macros, environment variables, subprocesses, networking, or filesystem writes.
- Accept exactly one CLI argument: a UTF-8 file path or `-` for stdin.
- Read input without modifying or executing it, and reject invalid UTF-8 instead of silently replacing or truncating bytes.
- Count every tab character and report one-based line numbers for lines containing tabs.
- Write the report to stdout and actionable failures to stderr; use a nonzero exit status for failures.
- Use Rust 1.90.0 with edition 2021 as the intended runner, without claiming a tested minimum version.

## Steps

- Save the single-file program as `recipe.rs`.
- Compile it with `rustc --edition=2021 recipe.rs -o recipe`.
- Run `./recipe path/to/saved.txt` to audit a file, or `./recipe -` and provide text on standard input.
- Check stdout for total tab count, affected-line count, and one-based line numbers; check stderr if the command reports a failure.

## Checks

- Compile using `rustc --edition=2021 recipe.rs -o recipe`.
- Pipe the synthetic example input to `./recipe -` and compare stdout exactly with the expected output.
- Try input containing no tabs and confirm the report says `tabs: 0`, `lines_with_tabs: 0`, and `line_numbers: none`.
- For the JSON-text fixture runner, test valid Unicode text including café and €; do not claim invalid-byte rejection from a UTF-8 JSON string. A separate raw-byte test must use byte 0xFF, expect exit 2 and stderr containing input is not valid UTF-8.
- Invoke the program with zero or two arguments and confirm stderr gives the usage form and the process exits nonzero.

## Limits

- The program reads the entire input into memory before validating UTF-8 and producing results.
- Line numbers are based on splitting at LF; a final LF creates an empty final segment, which cannot contain a tab.
- The tool only counts the literal tab character U+0009; it does not infer visual indentation or expand tabs.
- The input is treated as data only; this program does not parse document formats or interpret commands.
- Invalid-byte rejection requires a fixture containing raw invalid UTF-8 bytes. JSON text fixtures alone cannot demonstrate this case.

## Example input

```text
Synthetic stdin text, with a literal tab between `alpha` and `beta`:
alpha	beta
plain
x	y	z

```

## Expected output

```text
tabs: 3
lines_with_tabs: 2
line_numbers: 1,3

```

## Recorded validation scope

Executed 6 synthetic local fixture cases in isolated Rust 1.90.0 on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/str/fn.from_utf8.html
- https://doc.rust-lang.org/std/io/trait.Read.html
