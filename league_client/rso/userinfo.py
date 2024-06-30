from typing import Any
from typing import Optional

import httpx
from httpx._types import ProxyTypes

from league_client.constants import HEADERS


def get_userinfo(
    access_token: str, proxy: Optional[ProxyTypes] = None
) -> str | dict[str, Any]:
    h = HEADERS.copy()
    h["Authorization"] = f"Bearer {access_token}"
    res = httpx.post(
        "https://auth.riotgames.com/userinfo",
        headers=h,
        proxy=proxy,
    )
    res.raise_for_status()
    # userinfo can be either jwt or json based on access token type
    if res.headers["content-type"] == "application/jwt; charset=utf-8":
        return res.text
    return res.json()
