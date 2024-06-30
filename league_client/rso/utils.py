import json
from base64 import urlsafe_b64decode
from typing import Any

from league_client.rso.constants import PLAYER_PLATFORM_EDGE_URL


def decode_token(token: str) -> dict[str, Any]:
    payload = token.split(".")[1]
    info = urlsafe_b64decode(f"{payload}===")
    return json.loads(info)


def get_player_platform_url(region: str) -> str:
    return PLAYER_PLATFORM_EDGE_URL[region]
