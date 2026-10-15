# Validate JSON Arguments in Saved XML Tool Calls

Read a local XML workflow and report tool-call elements whose `arguments` attribute is not valid JSON, without executing or modifying the workflow.

Published recipe: [validate-xml-tool-argument-json](https://openvist.com/recipes/validate-xml-tool-argument-json/)

**Language:** python · **Version:** 0.1.1 · **License:** MIT

## Usage

Code file: `check_xml_arguments.py`

Save as `check_xml_arguments.py`. Run `python3 check_xml_arguments.py workflow.xml`; use `--tag action` if the file uses a different exact element name, or pass `-` to read XML from standard input. Intended runner: Python 3.12. No external packages, network access, credentials, or timeout configuration are needed; the program has no network calls.

## Requirements

- Use only Python standard-library interfaces documented by the supplied Python 3.12 sources: `argparse` for CLI arguments and `xml.etree.ElementTree` for XML parsing; `json` is used for embedded JSON validation.
- Read one user-supplied XML path or XML from standard input (`-`). Treat all file contents as data, not instructions.
- Inspect elements matching the exact CLI-selected tag; by default the tag is `tool_call`. Require an `arguments` attribute containing JSON, and report invalid or missing values by one-based matching-element position.
- Do not execute calls, modify files, contact external services, or print argument values. Write results to stdout and errors to stderr.
- Intended runner is Python 3.12; no minimum-version claim is made. The cited argparse documentation says argparse was added in Python 3.2, and the cited ElementTree documentation describes the XML parsing interfaces used here.
- ElementTree is not secure against maliciously constructed XML. Use only suitable, trusted local fixtures; this example does not claim to safely process hostile XML.

## Steps

- Save the proposed script as `check_xml_arguments.py`.
- Create a small XML fixture with several `tool_call` elements, including valid JSON, malformed JSON, and a missing `arguments` attribute.
- Run `python3 check_xml_arguments.py fixture.xml` and compare the reported positions with the fixture.
- Try a different exact element tag with `--tag action`, then verify that nonmatching elements are not counted.
- Pipe a valid XML fixture through standard input using `python3 check_xml_arguments.py -` and verify the summary.
- Try empty XML, malformed XML, and a nonexistent path; confirm each produces an error on stderr and a nonzero exit status.

## Checks

- With a fixture containing two matching elements—one with valid JSON and one with malformed JSON—confirm the malformed element is reported at position 2.
- With a matching element lacking `arguments`, confirm it is reported as invalid rather than accepted.
- With no matching elements, confirm the output reports zero matching elements and no invalid entries.
- With a malformed XML fixture, confirm parsing fails, an error is written to stderr, and the process exits nonzero.
- With a missing input path, confirm the missing-file error is reported on stderr and the process exits nonzero.
- Confirm that neither valid nor invalid JSON argument contents appear in output, and that no workflow call is executed.

## Limits

- This validates JSON syntax only. It does not check whether arguments match a tool schema, whether a tool exists, or whether a workflow is safe or executable.
- The default tag is the exact unnamespaced name `tool_call`; namespaced tags and alternate schemas require choosing a matching tag appropriate to the parsed XML.
- ElementTree skips comments, processing instructions, and document type declarations during parsing, as described by the supplied documentation.
- ElementTree is not secure against maliciously constructed data; this small example is for suitable local fixtures, not hostile XML.
- The parser reads the full XML input before reporting results; this is not a streaming or large-document tool.

## Example input

```text
<workflow>
  <tool_call arguments="{&amp;quot;city&amp;quot;:&amp;quot;Harborview&amp;quot;}" />
  <tool_call arguments="{&amp;quot;count&amp;quot;: }" />
  <tool_call />
</workflow>
```

## Expected output

```text
invalid: 2 of 3 matching elements
element 2: missing or invalid JSON arguments
element 3: missing or invalid JSON arguments
```

## Recorded validation scope

Executed 6 synthetic local fixture cases in isolated CPython 3.12.15 on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/xml.etree.elementtree.html
- https://docs.python.org/3.12/library/argparse.html
- https://docs.python.org/3.12/library/json.html
