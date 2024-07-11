from typing import Any
from typing import Optional

from httpx._types import ProxyTypes

from league_client.rso.constants import LootNameTypes
from league_client.rso.craft import craft


def disenchant_champion_shards(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    loot_data: dict[str, Any],
    proxy: Optional[ProxyTypes] = None,
):
    champion_shards = [
        item
        for item in loot_data["playerLoot"]  # ? ["lootItemList"]["lootItems"]
        if item["type"] in ["CHAMPION", "CHAMPION_RENTAL"]
    ]
    for shard in champion_shards:
        recipe_name = f"{shard['type'].split('_')[0]}_disenchant"
        if shard["lootName"] not in [item.value for item in LootNameTypes]:
            # prevent error, by skipping
            continue
        craft(
            ledge_token,
            ledge_url,
            puuid,
            recipe_name,
            [LootNameTypes(shard["lootName"])],
            1,
            proxy,
        )


def disenchant_eternals(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    loot_data: dict[str, Any],
    proxy: Optional[ProxyTypes] = None,
):
    eternals = [
        item
        for item in loot_data["playerLoot"]  # ? ["lootItemList"]["lootItems"]
        if item["type"] in ["STATSTONE_SHARD"]
    ]
    for eternal in eternals:
        if eternal["lootName"] not in [item.value for item in LootNameTypes]:
            # prevent error, by skipping
            continue
        craft(
            ledge_token,
            ledge_url,
            puuid,
            "STATSTONE_SHARD_DISENCHANT",
            [LootNameTypes(eternal["lootName"])],
            1,
            proxy,
        )


def disenchant_ward_skins(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    loot_data: dict[str, Any],
    proxy: Optional[ProxyTypes] = None,
):
    ward_skins = [
        item
        for item in loot_data["playerLoot"]  # ? ["lootItemList"]["lootItems"]
        if item["type"] in ["STATSTONE_SHARD"]
    ]
    for skin in ward_skins:
        if skin["lootName"] not in [item.value for item in LootNameTypes]:
            # prevent error, by skipping
            continue
        craft(
            ledge_token,
            ledge_url,
            puuid,
            "WARDSKIN_disenchant",
            [LootNameTypes(skin["lootName"])],
            1,
            proxy,
        )
