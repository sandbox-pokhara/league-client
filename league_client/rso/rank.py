from typing import Any
from typing import Optional

import httpx
from httpx._types import ProxyTypes

from league_client.constants import HEADERS


def get_rank_data(
    ledge_token: str,
    ledge_url: str,
    proxy: Optional[ProxyTypes] = None,
):
    h = HEADERS.copy()
    h["Authorization"] = f"Bearer {ledge_token}"
    res = httpx.get(
        f"{ledge_url}/leagues-ledge/v2/signedRankedStats",
        headers=h,
        proxy=proxy,
    )
    res.raise_for_status()
    return res.json()


def get_ranked_overview_token(
    rank_data: dict[str, Any],
):
    return rank_data["jwt"]
