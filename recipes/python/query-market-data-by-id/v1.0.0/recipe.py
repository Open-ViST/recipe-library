"""Query stable asset IDs with a CoinGecko Demo key supplied by your own environment."""
import json
import os
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

IDS = ["bitcoin", "ethereum", "solana"]
CURRENCY = "usd"


def get_prices(ids=IDS, currency=CURRENCY):
    ids = list(dict.fromkeys(ids))
    if not 1 <= len(ids) <= 10 or any(not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", value) for value in ids):
        raise ValueError("Use one to ten valid CoinGecko asset IDs.")
    if currency not in {"usd", "eur"}:
        raise ValueError("This example supports USD or EUR.")
    key = os.environ.get("COINGECKO_DEMO_API_KEY")
    if not key:
        raise RuntimeError("A CoinGecko Demo API key is required in your environment.")
    query = urlencode({"ids": ",".join(ids), "vs_currencies": currency, "include_last_updated_at": "true"})
    request = Request("https://api.coingecko.com/api/v3/simple/price?" + query, headers={"x-cg-demo-api-key": key})
    with urlopen(request, timeout=15) as reply:
        data = json.load(reply)
    if not isinstance(data, dict):
        raise RuntimeError("The provider response must be a JSON object.")
    missing = [asset for asset in ids if not isinstance(data.get(asset), dict) or type(data[asset].get(currency)) not in {int, float} or data[asset][currency] < 0]
    if missing:
        raise RuntimeError(f"Missing requested assets or prices: {missing}")
    return data


if __name__ == "__main__":
    print(json.dumps(get_prices(), indent=2))
