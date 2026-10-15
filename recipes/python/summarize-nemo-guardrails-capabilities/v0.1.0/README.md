# Summarize NeMo Guardrails’ documented safety capabilities

Print a concise, read-only summary of the safety capability names stated in the supplied NeMo Guardrails overview text.

Published recipe: [summarize-nemo-guardrails-capabilities](https://openvist.com/recipes/summarize-nemo-guardrails-capabilities/)

**Language:** python · **Version:** 0.1.0 · **License:** MIT

## Usage

Code file: `recipe.py`

See requirements below.

## Requirements

- Save the supplied official overview text as `nemo_guardrails_overview.txt` in the script’s working directory, encoded as UTF-8.
- The script uses only Python’s standard library; no package installation, credentials, network access, or NeMo Guardrails runtime is required.
- Capability names are matched as exact case-sensitive substrings, so this reports names present in that saved text, not a complete or version-independent feature inventory.

## Steps

- Save the overview text from the supplied source as `nemo_guardrails_overview.txt`.
- Save the example as `summarize_capabilities.py` in the same directory.
- Run `python summarize_capabilities.py` using Python 3.9 or later; this version floor is based on the standard-library features used, not a NeMo Guardrails requirement.
- Review the printed list against the source text; the script does not access the remote documentation or infer missing capabilities.

## Checks

- Confirm the input file exists, is UTF-8, and contains the expected overview excerpt; a missing or unreadable file should produce an error on standard error and a nonzero exit status.
- Check that the output contains only capability labels actually present in the supplied text, in the order listed in the script.
- Try a file containing none of the listed labels and confirm the script reports no matches and exits with status 2.
- Compare the result with the source text; exact substring matching can miss spelling or capitalization changes.

## Limits

- The supplied documentation establishes the listed safety approaches, but does not provide an endpoint for this task; therefore the example reads a local copy and makes no API request.
- The extracted list is deliberately limited to the exact capability labels visible in the provided overview text; it does not establish current support or behavior for a particular NeMo Guardrails release.
- The provided repository excerpt does not establish an exact release requirement for NeMo Guardrails, and this standalone text-processing example does not require that package.
- The sample is proposed code displayed as data and has not been run or tested; independently test it before publication.

## Recorded validation scope

Executed 4 synthetic local fixture cases in browser Python (Python 3.14.2 / browser Pyodide 314.0.7). All expected exit codes and declared output assertions passed. Live services, native system behavior and production deployment remain outside this scope.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.nvidia.com/nemo/guardrails/latest/
- https://github.com/NVIDIA/NeMo-Guardrails
