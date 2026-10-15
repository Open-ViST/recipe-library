# Query market data with stable asset IDs

Build a compact CoinGecko request using asset IDs, a target currency and an update timestamp.

Published recipe: [query-market-data-by-id](https://openvist.com/recipes/query-market-data-by-id/)

**Language:** python · **Version:** 1.0.0 · **License:** MIT

## Usage

Code file: `recipe.py`

See requirements below.

## Requirements

- Python 3.10 or later and access to the CoinGecko Demo API.
- A Demo API key supplied by your own environment as COINGECKO_DEMO_API_KEY.
- CoinGecko asset IDs checked against the provider’s coins list. Contract identity still comes from the relevant network and official project.

## Steps

- Choose one to ten asset IDs and select USD or EUR in the builder.
- Inspect the query. The example removes duplicate IDs and includes an update timestamp.
- Configure the Demo API key in your local environment and run the file once.
- Check last_updated_at and missing fields before using a returned value. Apply the provider’s attribution, rate and caching requirements to a deployed application.

## Checks

- Duplicate IDs produce one requested asset each.
- The key is a request header and does not enter the generated URL.
- Missing assets and HTTP failures are surfaced; no price is filled in from a placeholder.

## Limits

- The page does not display live market prices or make a market-data request.
- Provider IDs are not contract addresses. Match the chain and contract separately when needed.
- A timestamp is evidence to inspect, not an automatic guarantee that a price is current. Do not treat the sample as trading guidance.

## Recorded validation scope

Code syntax, query encoding, duplicate handling, request headers and mocked provider responses checked locally. No live provider request was made.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.coingecko.com/demo/reference/simple-price
- https://docs.coingecko.com/demo/reference/coins-list
