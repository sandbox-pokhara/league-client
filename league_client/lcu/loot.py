import json
import re
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import httpx

from league_client.logger import logger

SKIN_SHARD_RE = "CHAMPION_SKIN_RENTAL_[0-9]+"
SKIN_SHARD_PERMA_RE = "CHAMPION_SKIN_[0-9]+"


def get_loot(connection: httpx.Client) -> List[Dict[str, Any]]:
    try:
        res = connection.get("/lol-loot/v1/player-loot")
        res.raise_for_status()
        return res.json()
    except (
        httpx.HTTPStatusError,
        httpx.RequestError,
    ):
        return []


def get_player_loot_map(connection: httpx.Client) -> Dict[str, Any]:
    try:
        res = connection.get("/lol-loot/v1/player-loot-map/")
        res.raise_for_status()
        return res.json()
    except (
        httpx.HTTPStatusError,
        httpx.RequestError,
    ):
        return {}


def get_loot_count(connection: httpx.Client, loot_id: str) -> int:
    loot = get_loot(connection)
    if loot == []:
        return -1
    filtered_loot = [l for l in loot if l["lootId"] == loot_id]
    if filtered_loot == []:
        return 0
    return filtered_loot[0]["count"]


def get_loot_by_id(
    connection: httpx.Client, loot_id: str
) -> List[Dict[str, Any]]:
    try:
        res = connection.get(f"/lol-loot/v1/player-loot/{loot_id}")
        res.raise_for_status()
        return res.json()
    except (
        httpx.HTTPStatusError,
        httpx.RequestError,
    ):
        return []


def get_loot_name(loot: Dict[str, str]) -> str:
    if loot["localizedName"] != "":
        return loot["localizedName"]
    if loot["itemDesc"] != "":
        return loot["itemDesc"]
    return loot["lootId"]


def get_loot_by_pattern(
    connection: httpx.Client, pattern: str
) -> Optional[List[str]]:
    try:
        res = connection.get("/lol-loot/v1/player-loot-map/")
        res.raise_for_status()
        data = [
            s["storeItemId"]
            for s in res.json().values()
            if re.fullmatch(pattern, s["lootId"])
        ]
        return data
    except (
        httpx.HTTPStatusError,
        httpx.RequestError,
        Exception,
        json.JSONDecodeError,
        TypeError,
        re.error,
    ):
        logger.error(f"HTTP error occurred")
        return None


def get_eternals(connection: httpx.Client) -> List[Dict[str, str]]:
    loot = get_loot(connection)
    return [l for l in loot if l["type"] == "STATSTONE_SHARD"]


def get_ward_skins(connection: httpx.Client):
    loot = get_loot(connection)
    return [l for l in loot if l["type"].startswith("WARDSKIN_")]


def get_orange_essence(connection: httpx.Client) -> Optional[int]:
    try:
        res = connection.get("/lol-loot/v1/player-loot-map/")
        res.raise_for_status()
        loot_map = res.json()
        if "CURRENCY_cosmetic" not in loot_map:
            return 0
        return loot_map["CURRENCY_cosmetic"]["count"]
    except (
        httpx.HTTPStatusError,
        httpx.RequestError,
        Exception,
        json.JSONDecodeError,
        TypeError,
    ):
        logger.error(f"HTTP error occurred")
        return None


def get_skin_shards(connection: httpx.Client):
    return get_loot_by_pattern(connection, SKIN_SHARD_RE)


def get_perma_skin_shards(connection: httpx.Client):
    return get_loot_by_pattern(connection, SKIN_SHARD_PERMA_RE)


def get_key_fragment_count(connection: httpx.Client) -> int:
    return get_loot_count(connection, "MATERIAL_key_fragment")


def get_key_count(connection: httpx.Client) -> int:
    return get_loot_count(connection, "MATERIAL_key")


def get_generic_chest_count(connection: httpx.Client) -> int:
    return get_loot_count(connection, "CHEST_generic")


def get_champion_mastery_chest_count(connection: httpx.Client) -> int:
    return get_loot_count(connection, "CHEST_champion_mastery")


def get_masterwork_chest_count(connection: httpx.Client) -> int:
    return get_loot_count(connection, "CHEST_224")


def get_blue_essence_count(connection: httpx.Client) -> int:
    return get_loot_count(connection, "CURRENCY_champion")
