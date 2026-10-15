"""Call a model already installed on your own loopback LocalAI service."""
import json
from urllib.request import Request, urlopen

MODEL = "YOUR_INSTALLED_MODEL"
MAX_TOKENS = 256


def chat(model=MODEL, max_tokens=MAX_TOKENS):
    if model == "YOUR_INSTALLED_MODEL" or not model.strip():
        raise ValueError("Replace MODEL with a model ID returned by your local /v1/models endpoint.")
    if max_tokens not in {256, 512, 1024}:
        raise ValueError("Choose 256, 512 or 1024 tokens for this example.")
    body = {"model": model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": "Explain what a JSON object is in one sentence."}]}
    request = Request("http://127.0.0.1:8080/v1/chat/completions", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=30) as reply:
        data = json.load(reply)
    choices = data.get("choices") if isinstance(data, dict) else None
    message = choices[0].get("message") if isinstance(choices, list) and choices and isinstance(choices[0], dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content:
        raise RuntimeError("No assistant text was returned; inspect the model and backend logs.")
    return content


if __name__ == "__main__":
    print(chat())
