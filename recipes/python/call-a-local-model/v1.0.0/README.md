# Call an installed local model

Send a bounded chat request to your own LocalAI service and inspect the returned assistant text.

Published recipe: [call-a-local-model](https://openvist.com/recipes/call-a-local-model/)

**Language:** python · **Version:** 1.0.0 · **License:** MIT

## Usage

Code file: `recipe.py`

See requirements below.

## Requirements

- Python 3.10 or later and a running LocalAI service on 127.0.0.1:8080.
- A model already installed and listed by the service’s /v1/models endpoint.
- Hardware resources and a model licence appropriate for your use.

## Steps

- Follow the LocalAI installation instructions and confirm the service is available locally.
- List the installed models and replace YOUR_INSTALLED_MODEL with the exact model ID.
- Choose a token cap, inspect the code and run the file against your own service.
- Check the output and backend logs. Record your model, runtime and hardware before comparing results or exposing the service to another application.

## Checks

- The destination remains 127.0.0.1; changing a model cannot redirect the request.
- The placeholder is rejected and the maximum token setting is one of the documented choices.
- Missing assistant text causes an explicit error instead of a fabricated response.

## Limits

- The model must already be installed; the placeholder intentionally stops before a request.
- Running locally still consumes hardware, storage and maintenance time.
- This loopback example does not configure remote access, authentication, streaming or tool compatibility.

## Recorded validation scope

Code syntax, placeholder rejection, token caps and mocked local responses checked locally. No LocalAI runtime or model was started.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://localai.io/docs/installation/linux/
- https://localai.io/docs/features/text-generation/
