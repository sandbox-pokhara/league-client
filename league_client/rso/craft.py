import re
import time
import uuid
from typing import Any
from typing import Optional

import httpx
from httpx._types import ProxyTypes

from league_client.constants import HEADERS
from league_client.rso.constants import LootNameTypes
from league_client.rso.loot import get_champion_mastery_chest_count
from league_client.rso.loot import get_generic_chest_count
from league_client.rso.loot import get_key_count
from league_client.rso.loot import get_key_fragment_count
from league_client.rso.loot import get_loot_data
from league_client.rso.loot import get_masterwork_chest_count
from league_client.rso.loot import get_mythic_essence_count


def craft(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    recipe_name: str,
    loot_names: list[LootNameTypes],
    repeat: int = 1,
    proxy: Optional[ProxyTypes] = None,
):
    """Craft or open a chest item"""
    h = HEADERS.copy()
    h["Authorization"] = f"Bearer {ledge_token}"

    data = {
        "clientId": "LolClient-LEdge",
        "lootNameRefIds": [
            {"lootName": item, "refId": ""} for item in loot_names
        ],
        "recipeName": recipe_name,
        "repeat": repeat,
        "transactionId": str(uuid.uuid4()),
    }
    res = httpx.post(
        f"{ledge_url}/loot/v2/player/{puuid}/craft",
        headers=h,
        json=data,
        proxy=proxy,
    )
    res.raise_for_status()
    return res.json()


def craft_key_from_key_fragments(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    repeat: int = 1,
    proxy: Optional[ProxyTypes] = None,
):
    return craft(
        ledge_token,
        ledge_url,
        puuid,
        "MATERIAL_key_fragment_forge",
        [LootNameTypes.key_fragment],
        repeat,
        proxy,
    )


def craft_generic_chests(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    repeat: int = 1,
    proxy: Optional[ProxyTypes] = None,
):
    return craft(
        ledge_token,
        ledge_url,
        puuid,
        "CHEST_generic_OPEN",
        [LootNameTypes.generic_chest, LootNameTypes.key],
        repeat,
        proxy,
    )


def craft_champion_mastery_chest(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    repeat: int = 1,
    proxy: Optional[ProxyTypes] = None,
):
    return craft(
        ledge_token,
        ledge_url,
        puuid,
        "CHEST_champion_mastery_OPEN",
        [LootNameTypes.champion_mastery_chest, LootNameTypes.key],
        repeat,
        proxy,
    )


def craft_keys_and_generic_chests(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    retry_limit: int = 10,
    proxy: Optional[ProxyTypes] = None,
):
    for _ in range(retry_limit):

        loot_data = get_loot_data(ledge_token, ledge_url, puuid, proxy)

        forgable_keys = int(get_key_fragment_count(loot_data) / 3)
        key_count = get_key_count(loot_data)
        chest_count = get_generic_chest_count(loot_data)
        chest_count += get_champion_mastery_chest_count(loot_data)

        if (forgable_keys == 0 and key_count == 0) or chest_count == 0:
            return
        if forgable_keys > 0:
            craft_key_from_key_fragments(
                ledge_token, ledge_url, puuid, forgable_keys, proxy
            )
            time.sleep(0.5)

        if min(key_count, chest_count) > 0:
            craft_generic_chests(ledge_token, ledge_url, puuid, 1, proxy)
            craft_champion_mastery_chest(
                ledge_token, ledge_url, puuid, 1, proxy
            )
        time.sleep(0.5)


def craft_keys_and_masterwork_chests(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    retry_limit: int = 10,
    proxy: Optional[ProxyTypes] = None,
):
    for _ in range(retry_limit):
        loot_data = get_loot_data(ledge_token, ledge_url, puuid, proxy)

        forgable_keys = int(get_key_fragment_count(loot_data) / 3)
        key_count = get_key_count(loot_data)
        chest_count = get_masterwork_chest_count(loot_data)

        if (forgable_keys == 0 and key_count == 0) or chest_count == 0:
            return
        if forgable_keys > 0:
            craft_key_from_key_fragments(
                ledge_token, ledge_url, puuid, forgable_keys, proxy
            )
            time.sleep(0.5)
            continue

        if min(key_count, chest_count) > 0:
            craft_generic_chests(ledge_token, ledge_url, puuid, 1, proxy)
            craft_champion_mastery_chest(
                ledge_token, ledge_url, puuid, 1, proxy
            )
        time.sleep(0.5)


def craft_chest_by_loot_name(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    loot_name: LootNameTypes,
    requires_key: bool = False,
    repeat: int = 1,
    proxy: Optional[ProxyTypes] = None,
):
    """Craft or open an chest item by loot id"""
    loot_names = [loot_name]
    if requires_key:
        loot_names.append(LootNameTypes.key)
    return craft(
        ledge_token,
        ledge_url,
        puuid,
        f"{loot_name}_OPEN",
        loot_names,
        repeat,
        proxy,
    )


def craft_chest_loots(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    loot_data: dict[str, Any],
    requires_key: bool = True,
    delay: int = 1,
    proxy: Optional[ProxyTypes] = None,
):
    key_count = 0
    if requires_key:
        key_count: int = get_key_count(loot_data)
    loot: dict[str, Any]
    for loot in loot_data["playerLoot"]:
        count: int = loot["count"]
        if requires_key:
            if key_count == 0:
                return
            count: int = min(count, key_count)
        craft_chest_by_loot_name(
            ledge_token,
            ledge_url,
            puuid,
            loot["lootName"],
            requires_key,
            count,
            proxy,
        )
        if delay > 0:
            time.sleep(delay)


def craft_champion_capsules(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    delay: int = 1,
    proxy: Optional[ProxyTypes] = None,
):
    loot_data = get_loot_data(ledge_token, ledge_url, puuid, proxy)
    champion_capsules = [
        item
        for item in loot_data["playerLoot"]
        if re.fullmatch(
            "CHEST_((?!(generic|224|champion_mastery)).)*", item["lootName"]
        )
    ]
    craft_chest_loots(
        ledge_token,
        ledge_url,
        puuid,
        {"playerLoot": champion_capsules},
        False,
        delay,
        proxy,
    )


def craft_mythic_essence_into_skin_shard(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    proxy: Optional[ProxyTypes] = None,
):
    loot_data = get_loot_data(ledge_token, ledge_url, puuid, proxy)
    count: int = get_mythic_essence_count(loot_data)
    if count < 10:
        return
    return craft(
        ledge_token,
        ledge_url,
        puuid,
        "CURRENCY_mythic_forge_13",
        [LootNameTypes.mythic_essence],
        count // 10,
        proxy,
    )
