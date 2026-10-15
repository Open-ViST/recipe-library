# Count Lines in a Local UTF-8 File or Standard Input

Create a Rust 2021 CLI that streams one UTF-8 file or standard input (`-`) and reports total, blank, and nonblank line counts. Propagate I/O and UTF-8 errors instead of silently truncating input.

Published recipe: [rust-stream-line-counts](https://openvist.com/recipes/rust-stream-line-counts/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

Intended runner: Rust 1.90.0, edition 2021. Compile with `rustc --edition=2021 recipe.rs -o recipe`. Run `./recipe PATH` to read a file or `./recipe -` to read standard input. The output format is exactly three lines, in order: `total: N`, `blank: N`, `nonblank: N`. Errors are written to stderr and use a nonzero exit status.

## Requirements

- Use only Rust standard-library APIs.
- Accept exactly one argument: a UTF-8 file path or `-` for standard input.
- Stream input through a buffered reader and do not collect all lines.
- Count a final unterminated line as a line.
- Classify a line as blank when every character is Unicode whitespace; the empty string is blank.
- Treat invalid UTF-8 and read failures as errors; do not silently return partial counts.
- Print counts to stdout in the documented stable order and send actionable errors to stderr.
- Do not modify the input file or treat its contents as instructions.

## Steps

- Save the single-file program as `recipe.rs`.
- Compile it with `rustc --edition=2021 recipe.rs -o recipe` using the intended Rust 1.90.0 runner.
- Run `./recipe PATH` with a UTF-8 fixture, or pipe fixture text to `./recipe -`.
- Compare stdout with the documented `total`, `blank`, and `nonblank` format.
- Check error handling with a nonexistent path and with malformed UTF-8 input.

## Checks

- Run `./recipe -` with empty stdin and confirm the output is exactly `total: 0`, `blank: 0`, `nonblank: 0`, each on its own line.
- Run the synthetic Unicode example through stdin and confirm the documented exact output.
- Test a file containing a final nonempty line without a trailing newline and verify that it is counted.
- Try a nonexistent file path; confirm an actionable stderr error and nonzero exit status.
- Feed malformed UTF-8 through stdin; confirm the program reports an error and does not print partial counts as a successful result.
- Invoke with zero or multiple arguments and confirm the usage message is written to stderr.

## Limits

- The program counts lines; it does not retain or print line contents.
- A line containing only Unicode whitespace is considered blank; other Unicode classification details follow Rust's `char::is_whitespace`.
- The standard `BufRead::lines` API decodes each line as UTF-8, so malformed input is an error.
- Counts use `u64`; inputs exceeding that count are outside the intended practical use.
- No behavior for concurrent input changes or special device files beyond ordinary standard-library I/O guarantees is promised.

## Example input

```text
Synthetic stdin input, supplied to `./recipe -`:

<empty line>
Rust
  
雪

The input has four lines: an empty line, `Rust`, a line containing two spaces, and `雪` (with a final newline).
```

## Expected output

```text
total: 4
blank: 2
nonblank: 2
```

## Recorded validation scope

Executed 5 synthetic local fixture cases in isolated Rust 1.90.0 on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/stable/rust-by-example/std_misc/file/read_lines.html
- https://doc.rust-lang.org/std/io/trait.BufRead.html
- https://github.com/rust-lang/rust-by-example/blob/dcc14f912bf8790792a2df082eddc82ab2539229/src/std_misc/file/read_lines.md
- https://github.com/rust-lang/rust-by-example/blob/dcc14f912bf8790792a2df082eddc82ab2539229/LICENSE-MIT

## Attribution

See UPSTREAM-NOTICE.txt for the original copyright and MIT license notice.
