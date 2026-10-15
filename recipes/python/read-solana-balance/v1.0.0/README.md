# Build a read-only Solana balance tool

Create a small balance reader with an explicit network, public account and commitment level.

Published recipe: [read-solana-balance](https://openvist.com/recipes/read-solana-balance/)

**Language:** python · **Version:** 1.0.0 · **License:** MIT

## Usage

Code file: `recipe.py`

See requirements below.

## Requirements

- Python 3.10 or later; this example uses only its standard library.
- A base58 public account address that decodes to 32 bytes.
- Access to the selected Solana RPC endpoint. Public endpoints have rate limits.

## Steps

- Start on Devnet and choose the commitment required by your application.
- Change the account field and inspect the generated request and validation function.
- Run the file and keep the network, commitment, lamports and context together.
- Before attaching the function to an agent, define the allowed arguments and handle RPC errors, timeouts and rate limits in the host application.

## Checks

- Only getBalance is requested; no transaction or signing method is present.
- Invalid addresses and unsupported networks are rejected before a network request.
- Large lamport values remain integers, and a JSON-RPC error stops processing.

## Limits

- This recipe does not sign or submit transactions and does not need a private key.
- Devnet and Mainnet beta are separate networks. A balance on one is not a balance on the other.
- Keep lamports as an integer. The preview validates the address shape and length, not the account’s purpose or existence.

## Recorded validation scope

Code syntax, address validation, network selection and mocked RPC responses checked locally. No agent integration or live RPC execution is claimed.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://solana.com/docs/rpc/http/getbalance
- https://solana.com/docs/rpc
- https://developers.openai.com/api/docs/guides/function-calling
