import json
from base64 import urlsafe_b64decode
from typing import Any


def decode_token(token: str) -> dict[str, Any]:
    payload = token.split(".")[1]
    info = urlsafe_b64decode(f"{payload}===")
    return json.loads(info)
