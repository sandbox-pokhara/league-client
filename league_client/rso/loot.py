from typing import Any

import httpx

from league_client.constants import HEADERS
from league_client.rso.models import RSOSession


def get_loot(session: RSOSession):
    h = HEADERS.copy()
    h["Authorization"] = f"Bearer {session.ledge_token}"
    url = session.get_ledge_url(
        f"/loot/v2/player/{session.puuid}/loot/definitions"
    )
    res = httpx.get(
        url,
        headers=h,
        proxy=session.proxy,
    )
    res.raise_for_status()
    return res.json().get("playerLoot", {})


def get_loot_count(loot: list[dict[str, Any]], loot_id: str):
    filtered_loot = [l for l in loot if l["lootName"] == loot_id]
    if filtered_loot == []:
        return 0
    return filtered_loot[0]["count"]


def get_key_fragment_count(loot: list[dict[str, Any]]):
    return get_loot_count(loot, "MATERIAL_key_fragment")


def get_key_count(loot: list[dict[str, Any]]):
    return get_loot_count(loot, "MATERIAL_key")


def get_generic_chest_count(loot: list[dict[str, Any]]):
    return get_loot_count(loot, "CHEST_generic")


def get_champion_mastery_chest_count(loot: list[dict[str, Any]]):
    return get_loot_count(loot, "CHEST_champion_mastery")


def get_masterwork_chest_count(loot: list[dict[str, Any]]):
    return get_loot_count(loot, "CHEST_224")


def get_blue_essence_count(loot: list[dict[str, Any]]):
    return get_loot_count(loot, "CURRENCY_champion")


def get_orange_essence_count(loot: list[dict[str, Any]]):
    return get_loot_count(loot, "CURRENCY_cosmetic")
