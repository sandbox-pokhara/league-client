from typing import Optional

import httpx
from httpx._types import ProxyTypes

from league_client.constants import HEADERS


def get_loot_data(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    proxy: Optional[ProxyTypes] = None,
):
    h = HEADERS.copy()
    h["Authorization"] = f"Bearer {ledge_token}"
    res = httpx.get(
        f"{ledge_url}/loot/v2/player/{puuid}/loot/definitions",
        headers=h,
        proxy=proxy,
    )
    res.raise_for_status()
    return res.json()
