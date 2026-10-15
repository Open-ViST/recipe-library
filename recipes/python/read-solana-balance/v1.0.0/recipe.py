"""Read an account balance without signing or sending a transaction."""
import json
from urllib.request import Request, urlopen

NETWORK = "devnet"
COMMITMENT = "finalized"
ADDRESS = "11111111111111111111111111111111"
ENDPOINTS = {"devnet": "https://api.devnet.solana.com", "mainnet-beta": "https://api.mainnet-beta.solana.com"}


def validate_address(address):
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    if not 32 <= len(address) <= 44 or any(c not in alphabet for c in address):
        raise ValueError("Expected a base58 public account address.")
    number = 0
    for char in address:
        number = number * 58 + alphabet.index(char)
    decoded_length = (number.bit_length() + 7) // 8 + len(address) - len(address.lstrip("1"))
    if decoded_length != 32:
        raise ValueError("Expected a 32-byte public account address.")


def get_balance(address=ADDRESS, network=NETWORK, commitment=COMMITMENT):
    validate_address(address)
    if network not in ENDPOINTS or commitment not in {"processed", "confirmed", "finalized"}:
        raise ValueError("Unsupported network or commitment.")
    body = {"jsonrpc": "2.0", "id": 1, "method": "getBalance", "params": [address, {"commitment": commitment}]}
    request = Request(ENDPOINTS[network], data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=15) as reply:
        data = json.load(reply)
    if not isinstance(data, dict):
        raise RuntimeError("The RPC response must be a JSON object.")
    if "error" in data:
        raise RuntimeError(f"RPC error: {data['error']}")
    result = data.get("result")
    value = result.get("value") if isinstance(result, dict) else None
    if type(value) is not int or value < 0:
        raise RuntimeError("RPC response did not contain a non-negative lamport balance.")
    return {"network": network, "commitment": commitment, "address": address, "lamports": value, "context": data["result"].get("context", {})}


if __name__ == "__main__":
    print(json.dumps(get_balance(), indent=2))
