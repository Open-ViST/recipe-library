# Validate the Root and Required Fields of a Saved XML Agent Workflow

Read a local XML workflow and validate that its root has an exact CLI-selected tag and that every element with an exact CLI-selected call tag has nonempty `name` and `arguments` attributes, without executing or modifying the workflow.

Published recipe: [validate-xml-agent-workflow-structure](https://openvist.com/recipes/validate-xml-agent-workflow-structure/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `validate_workflow.py`

Save as `validate_workflow.py`, then run `python3.12 validate_workflow.py workflow.xml --root-tag workflow --call-tag tool_call`. Use `-` as the file argument to read stdin, for example `python3.12 validate_workflow.py - --root-tag workflow --call-tag tool_call < workflow.xml`.

## Requirements

- Intended runner: Python 3.12; no minimum version claim is made.
- Uses only Python standard-library `argparse`, `sys`, `pathlib`, and `xml.etree.ElementTree`, whose documented interfaces support CLI parsing and XML parsing/iteration.
- Input must be a local UTF-8 XML file or XML supplied on stdin. No credentials, network access, remote changes, or output files are used.
- ElementTree documentation warns it is not secure against maliciously constructed XML. Use only appropriate trusted local fixtures; this validator is not a security boundary.

## Steps

- Save the code in a local file named `validate_workflow.py`.
- Create the synthetic XML fixture shown above as `workflow.xml`.
- Run the command in `usage` and confirm it prints the expected success line.
- Change one call to omit `name` or provide only whitespace in `arguments`; confirm it prints an `INVALID` diagnostic and exits unsuccessfully.
- Change the root tag or use a different `--root-tag`; confirm the root mismatch is reported.
- Try an empty file and malformed XML; confirm parsing errors are reported. Try a nonexistent path and invalid UTF-8 bytes; confirm each is reported as an input error.
- Pipe the valid fixture through stdin using the documented `-` form and confirm it produces the same validation result.

## Checks

- Run the valid synthetic fixture and compare stdout exactly with `OK: root=workflow; 2 call element(s) validated`.
- Use a syntactically valid XML fixture with a wrong root and verify the expected-versus-actual root diagnostic.
- Use a call element with a missing or whitespace-only required attribute and verify its one-based call number and attribute name are reported, without printing attribute values.
- Test empty and malformed XML separately; verify each yields a clear error on stderr and a nonzero exit status.
- Test a missing file and invalid UTF-8 input; verify both fail without a traceback.
- Run the same valid XML through stdin and a path; verify equivalent success output. Independently test all behavior before publication.

## Limits

- Checks exact XML tag names and attribute presence/nonblankness only; namespace-qualified tags must be supplied in their exact parsed form and are not specially normalized.
- Does not parse or validate the contents of `arguments`, resolve workflow references, infer framework-specific schemas, execute calls, or prove a workflow safe or operational.
- ElementTree parses the full document into memory, so this is for modest local workflow files rather than streaming very large XML.
- The example is proposed code displayed as data and requires independent testing before publication; no execution or testing is claimed.

## Example input

```text
<workflow>
  <tool_call name="lookup" arguments="{&quot;key&quot;:&quot;sample&quot;}" />
  <tool_call name="summarize" arguments="{}" />
</workflow>
```

## Expected output

```text
OK: root=workflow; 2 call element(s) validated
```

## Recorded validation scope

Executed 6 synthetic local fixture cases in isolated CPython 3.12.15 on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/xml.etree.elementtree.html
- https://docs.python.org/3.12/library/argparse.html
