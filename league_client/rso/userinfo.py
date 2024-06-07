from typing import Optional

import httpx
from httpx._types import ProxyTypes

from league_client.constants import HEADERS
from league_client.rso.auth import Auth


def get_userinfo(auth: Auth, proxy: Optional[ProxyTypes] = None):
    h = HEADERS.copy()
    h["Authorization"] = f"{auth.token_type} {auth.access_token}"
    res = httpx.post(
        "https://auth.riotgames.com/userinfo",
        headers=h,
        proxy=proxy,
    )
    res.raise_for_status()
    return res.json()
