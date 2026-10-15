# Check Local XML Workflow References

Read an XML workflow file and report elements whose `ref` attribute points to no declared `id`, without executing or modifying the workflow.

Published recipe: [validate-xml-workflow-reference-links](https://openvist.com/recipes/validate-xml-workflow-reference-links/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `check_refs.py`

Save as `check_refs.py`, then run `python3.12 check_refs.py workflow.xml` or pipe a fixture with `cat workflow.xml | python3.12 check_refs.py -`. The program reads the whole XML document; it makes no network calls and performs no retries.

## Requirements

- Python 3.12 is the intended runner; no minimum-version claim is made.
- Uses only Python standard-library `argparse`, `sys`, `pathlib`, and `xml.etree.ElementTree`.
- Input must be UTF-8 XML supplied as a local file or stdin. XML is treated strictly as data, not instructions.
- The check defines a reference as an exact, nonempty `ref` attribute matching any nonempty `id` attribute anywhere in the document; it does not apply namespaces, schema rules, or workflow-specific semantics.
- ElementTree is not secure against maliciously constructed XML. Use only trusted fixtures; this example is not a hardened parser for untrusted XML.
- The displayed code is a proposal and requires independent testing before publication.

## Steps

- Save the code as `check_refs.py`.
- Create a synthetic XML file containing at least one declared `id`, one matching `ref`, and one dangling `ref`.
- Run `python3.12 check_refs.py fixture.xml` and confirm only the dangling reference is reported.
- Run `python3.12 check_refs.py -` and provide the same XML through standard input; confirm the same result.
- Try a well-formed XML document with no unresolved references and confirm the clean-result message.
- Try empty input and malformed XML; confirm a parse error is written to stderr and the command returns a nonzero status.
- Try a nonexistent file path; confirm the missing-file error is reported without a traceback.

## Checks

- Use a fixture with two declared IDs and references to one existing and one absent ID; verify only the absent one is reported.
- Use a fixture with no `ref` attributes; verify the no-unresolved-references message.
- Use empty stdin and malformed XML; verify a readable error, nonzero exit status, and no partial success output.
- Use a nonexistent path; verify the missing-file error and nonzero exit status.
- Confirm the tool does not write to or modify its input fixture.

## Limits

- Checks only exact `id`/`ref` attribute matches; it does not infer links from element text or other attributes.
- Does not validate XML against a schema, detect duplicate IDs, interpret namespaces specially, or determine workflow correctness.
- ElementTree parses the entire document in memory and the documented API warns it is not secure against maliciously constructed data.
- No timeout is applicable: the tool makes no network calls.

## Example input

```text
<workflow><node id="start"/><link ref="start"/><link ref="missing"/></workflow>
```

## Expected output

```text
unresolved ref='missing' on <link>
```

## Recorded validation scope

Executed 5 synthetic local fixture cases in isolated CPython 3.12.15 on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/xml.etree.elementtree.html
- https://docs.python.org/3.12/library/argparse.html
