from typing import Any
from typing import Optional

import httpx
from httpx._types import ProxyTypes

from league_client.constants import HEADERS
from league_client.rso.constants import LootNameTypes


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


def get_loot_count(loot_data: dict[str, Any], loot_name: str):
    # return first item.count or 0
    return next(
        (
            item["count"]
            for item in loot_data["playerLoot"]
            if item["lootName"] == loot_name
        ),
        0,
    )


def get_key_fragment_count(loot_data: dict[str, Any]):
    return get_loot_count(loot_data, LootNameTypes.key_fragment)


def get_key_count(loot_data: dict[str, Any]):
    return get_loot_count(loot_data, LootNameTypes.key)


def get_generic_chest_count(loot_data: dict[str, Any]):
    return get_loot_count(loot_data, LootNameTypes.generic_chest)


def get_champion_mastery_chest_count(loot_data: dict[str, Any]):
    return get_loot_count(loot_data, LootNameTypes.champion_mastery_chest)


def get_masterwork_chest_count(loot_data: dict[str, Any]):
    return get_loot_count(loot_data, LootNameTypes.masterwork_chest)


def get_blue_essence_count(loot_data: dict[str, Any]):
    return get_loot_count(loot_data, LootNameTypes.blue_essence)


def get_orange_essence_count(loot_data: dict[str, Any]):
    return get_loot_count(loot_data, LootNameTypes.orange_essence)


def get_mythic_essence_count(loot_data: dict[str, Any]):
    return get_loot_count(loot_data, LootNameTypes.mythic_essence)
