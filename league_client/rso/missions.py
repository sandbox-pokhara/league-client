from typing import Optional

import httpx
from httpx._types import ProxyTypes

from league_client.constants import HEADERS


def get_missions(
    ledge_token: str,
    ledge_url: str,
    inventory_tokens: list[str],  # list of `EVENT_PASS, CHAMPION_SKIN` tokens
    userinfo_token: str,
    proxy: Optional[ProxyTypes] = None,
):
    h = HEADERS.copy()
    h["Authorization"] = f"Bearer {ledge_token}"
    res = httpx.put(
        f"{ledge_url}/missions/v5/player",
        headers=h,
        json={
            "level": 30,
            "loyaltyEnabled": False,
            "playerInventory": {
                "champions": [],
                "icons": [],
                "inventoryJwts": inventory_tokens,
                "skins": [],
                "wardSkins": [],
            },
            "userInfoToken": userinfo_token,
        },
        proxy=proxy,
    )
    res.raise_for_status()
    return res.json()
