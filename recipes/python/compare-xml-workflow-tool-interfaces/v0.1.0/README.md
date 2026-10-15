# Compare Tool Interfaces in Two Saved XML Workflows

Read two local XML workflow files and report tool elements whose tag-and-attribute signatures appear in only one file, without executing or modifying either workflow.

Published recipe: [compare-xml-workflow-tool-interfaces](https://openvist.com/recipes/compare-xml-workflow-tool-interfaces/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `compare_tools.py`

Save the code as compare_tools.py, then run `python3.12 compare_tools.py before.xml after.xml`. It reads both named local files, prints JSON to standard output, and reports file or XML parse errors to standard error with a nonzero exit status. Python 3.12 is the intended runner; no minimum-version claim is made.

## Requirements

- Use Python 3.12 as the intended runner; this recipe makes no claim about a tested minimum version.
- The Python standard library modules argparse, json, sys, pathlib, and xml.etree.ElementTree are sufficient; no installation, credentials, or network access are required.
- Provide two readable, well-formed XML files. ElementTree is not secure against maliciously constructed XML; use only trusted local fixtures.
- The tool identifies elements whose exact case-sensitive local tag name is `tool`; namespaced tool tags are matched by local name but reported with their original qualified tag.

## Steps

- Save the script as `compare_tools.py`.
- Create two small XML fixtures representing the earlier and later workflow structures.
- Run `python3.12 compare_tools.py before.xml after.xml` with the fixture paths as positional arguments.
- Review the `added` and `removed` JSON arrays; an empty array means no signature differences in that direction.
- Change one tool attribute in a fixture and rerun to confirm the old signature is removed and the changed signature is added.

## Checks

- Run with identical valid files and confirm both arrays are empty.
- Run the synthetic before/after example and confirm only the `quote` signature is listed under `added`.
- Change the `mode` attribute on an existing tool and confirm the former signature appears under `removed` and the changed one under `added`.
- Try a well-formed XML document with no tool elements and confirm the output contains two empty arrays.
- Try an empty file or malformed XML and confirm an error is written to standard error with a nonzero exit status.
- Try a nonexistent input path and confirm the missing-file error is reported without producing a comparison result.

## Limits

- This is a structural XML comparison, not a workflow validator or an execution test; it does not establish that any tool works or that an external service is available.
- Only elements with the exact local tag name `tool` are considered; other possible tool-node conventions are not inferred.
- Signatures include all attributes, so changing any attribute produces an added and removed entry. Text, child elements, namespaces beyond the original tag string, and ordering among repeated identical signatures are not compared.
- Repeated identical tool signatures collapse to one set entry; this tool compares distinct signatures, not occurrence counts.
- XML parsing reads each document as a whole. Do not use this small recipe for very large documents or untrusted XML.

## Example input

```text
before.xml:
<workflow><tool name="lookup" mode="read"/><step/></workflow>

after.xml:
<workflow><tool name="lookup" mode="read"/><tool name="quote" mode="read"/></workflow>
```

## Expected output

```text
{
  "added": [
    {
      "tag": "tool",
      "attributes": {
        "mode": "read",
        "name": "quote"
      }
    }
  ],
  "removed": []
}
```

## Recorded validation scope

Executed 5 synthetic local fixture cases in isolated CPython 3.12.15 on GitHub Actions, without network access. Declared exit codes, output assertions and input integrity checks passed. Live services, installed third-party packages and production behavior remain outside scope. Editorial approval is still required.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3.12/library/xml.etree.elementtree.html
- https://docs.python.org/3.12/library/argparse.html
