# Summarize Saved Text by Final-Character Group

Read one UTF-8 text file or standard input and report how many nonblank lines end with each Unicode character, using case-sensitive, exact grouping. Ignore leading and trailing whitespace when determining each line’s final character; do not modify or execute the input.

Published recipe: [summarize-saved-text-by-final-character](https://openvist.com/recipes/summarize-saved-text-by-final-character/)

**Language:** rust · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.rs`

Compile with `rustc --edition=2021 recipe.rs -o recipe`. Run `./recipe <UTF-8-file>` to read a file or `./recipe -` to read standard input. Provide exactly one argument. The program does not interpret input as instructions or write to files.

## Requirements

- Intended runner: Rust 1.90.0, edition 2021; this is not a claim about the minimum supported Rust version.
- Standard library only; no external crates, unsafe code, include macros, environment-variable access, threads, networking, subprocesses, or filesystem writes.
- Accept exactly one CLI argument: a UTF-8 file path or `-` for standard input.
- Treat all input as untrusted, read-only UTF-8 text; propagate I/O and decoding failures instead of silently truncating input.
- Count a line as nonblank when its Unicode-whitespace-trimmed content is nonempty; use its last remaining Unicode scalar value as the grouping key.
- Write counts and character groups to stdout, and actionable errors to stderr. Exit nonzero only for actionable failures.

## Steps

- Create `recipe.rs` and place the complete Rust program from the example code in it.
- Compile using `rustc --edition=2021 recipe.rs -o recipe`.
- Run `./recipe -` and enter the example text followed by end-of-file, or save equivalent UTF-8 text and run `./recipe path/to/file.txt`.
- Check that grouping ignores surrounding whitespace, preserves character case, and prints character groups in sorted order.
- Try a nonexistent path and confirm that the program prints a useful error to stderr and exits nonzero.

## Checks

- Compile with `rustc --edition=2021 recipe.rs -o recipe`.
- Pipe the synthetic example input to `./recipe -` and compare stdout exactly with the expected output.
- Try input containing uppercase and lowercase final characters and verify they form separate groups.
- Try an all-whitespace input and verify the output is `nonblank_lines: 0` with no character-group lines.
- Try a file with invalid UTF-8 and verify the error is reported on stderr and processing fails.
- Try invoking the program with no arguments or multiple arguments and verify the usage error is actionable.

## Limits

- Counts are held in `usize`; the program is intended for ordinary saved-text inspection, not guaranteed to handle inputs exceeding available memory or runtime limits.
- `BufRead::lines` removes line terminators and reports invalid UTF-8 or read errors; a failure stops processing rather than producing partial success output.
- Each line is grouped by its final non-whitespace Unicode scalar value, not by grapheme cluster; a visible character composed of multiple scalar values may therefore be grouped by its final scalar.
- A line containing only Unicode whitespace is excluded.
- Character labels use Rust char::escape_default: non-ASCII scalar values are printed as hexadecimal Unicode escapes such as \u{f1}; ordering follows scalar values.
- The recorded five-case execution did not test malformed UTF-8 bytes or multiple CLI arguments. Those checks are additional manual instructions, not executed coverage claims.

## Example input

```text
Input supplied on standard input using `./recipe -`:

Apple
pear!
  tea  


```

## Expected output

```text
nonblank_lines: 3
!: 1
a: 1
e: 1

```

## Recorded validation scope

Executed 5 synthetic local fixture cases in isolated Rust 1.90.0 on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://doc.rust-lang.org/std/io/trait.BufRead.html
- https://doc.rust-lang.org/std/collections/index.html
