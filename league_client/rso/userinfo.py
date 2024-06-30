from typing import Any
from typing import Optional

import httpx
from httpx._types import ProxyTypes

from league_client.constants import HEADERS
from league_client.rso.auth import Auth
from league_client.rso.auth import AuthLol


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


def get_userinfo_token(auth_lol: AuthLol, proxy: Optional[ProxyTypes] = None):
    h = HEADERS.copy()
    h["Authorization"] = f"{auth_lol.token_type} {auth_lol.access_token}"
    res = httpx.post(
        "https://auth.riotgames.com/userinfo",
        headers=h,
        proxy=proxy,
    )
    res.raise_for_status()
    return str(res.text)


def get_puuid(decoded_access_token: dict[str, Any]) -> str:
    return decoded_access_token["sub"]


def get_region(decoded_access_token: dict[str, Any]) -> str:
    return decoded_access_token["dat"]["r"]
