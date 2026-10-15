# Extract a small project record as JSON

Turn a short description into a typed record and adjust the fields you want to keep.

Published recipe: [extract-project-json](https://openvist.com/recipes/extract-project-json/)

**Language:** python · **Version:** 1.0.0 · **License:** MIT

## Usage

Code file: `recipe.py`

See requirements below.

## Requirements

- Python 3.10 or later, the official OpenAI Python SDK and Pydantic 2.
- Your own provider API access and a configured runtime environment. The downloaded script makes one paid request.
- A small source description. Do not put private account details into the example.

## Steps

- Inspect the default code, then toggle the optional fields and compare the Project model.
- Install the dependencies in an isolated Python environment and configure your provider access using its secure settings.
- Run the file once. Keep the parsed result only when the response completed and a parsed object exists.
- Compare every value with the original text. Empty lists are appropriate when a requirement or source was not stated.

## Checks

- The Project fields match the selected checkboxes.
- A completed response has a parsed object, and missing facts were not invented.
- The request is made only in your Python environment; copying and previewing the code make no request.

## Limits

- A schema is a format guarantee, not factual verification.
- Refusals, incomplete responses and network failures still need handling. This example stops instead of retrying silently.
- The model, service tier and output cap are explicit. Check the provider’s current pricing before running.

## Recorded validation scope

Code syntax and all four field combinations checked locally. The API example was tested with a mocked SDK response, not executed against the provider.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses
- https://github.com/openai/openai-python/blob/main/helpers.md
