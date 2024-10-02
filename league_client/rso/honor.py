from typing import Any
from typing import Optional

import httpx

from league_client.constants import HEADERS
from league_client.types import ProxyT


def get_honor_data(
    ledge_token: str,
    ledge_url: str,
    proxy: Optional[ProxyT] = None,
):
    h = HEADERS.copy()
    h["Authorization"] = f"Bearer {ledge_token}"
    res = httpx.get(
        f"{ledge_url}/honor-edge/v2/retrieveProfileInfo/",
        headers=h,
        proxy=proxy,
    )
    res.raise_for_status()
    return res.json()


def get_honor_level(
    honor_data: dict[str, Any],
):
    return honor_data["honorLevel"]
