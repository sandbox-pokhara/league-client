from typing import Any
from typing import Optional
from typing import cast

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


def get_tier_division_wins_losses(
    rank_data: dict[str, Any],
    queue_type: str = "RANKED_SOLO_5x5",
):
    # queue types:
    # RANKED_SOLO_5x5, RANKED_FLEX_SR, RANKED_TFT, RANKED_TFT_TURBO
    # RANKED_TFT_DOUBLE_UP, CHERRY
    item: dict[str, Any] = next(
        (q for q in rank_data["queues"] if q["queueType"] == queue_type),
        cast(dict[str, Any], {}),
    )
    tier = item.get("tier", "UNRANKED")
    division = item.get("rank", None)
    wins = item.get("wins", 0)
    losses = item.get("losses", 0)
    return tier, division, wins, losses
