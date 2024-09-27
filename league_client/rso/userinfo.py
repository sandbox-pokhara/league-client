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
    # riot server sends either application/jwt;charset=UTF-8 or
    # application/jwt; charset=utf-8 for jwt tokens
    if res.headers["content-type"].lower().startswith("application/jwt;"):
        return res.text
    return res.json()
