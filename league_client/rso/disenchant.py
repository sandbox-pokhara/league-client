from typing import Any
from typing import Optional

from httpx._types import ProxyTypes

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
        if item["lootItemType"] in ["CHAMPION", "CHAMPION_RENTAL"]
    ]
    for shard in champion_shards:
        recipe_name = f"{'CHAMPION_RENTAL' if 'CHAMPION_RENTAL' in shard['lootItemType'] else 'CHAMPION'}_disenchant"
        craft(
            ledge_token,
            ledge_url,
            puuid,
            recipe_name,
            [shard["lootName"]],
            shard["count"],
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
        if item["lootItemType"] in ["STATSTONE_SHARD"]
    ]
    for eternal in eternals:
        craft(
            ledge_token,
            ledge_url,
            puuid,
            "STATSTONE_SHARD_DISENCHANT",
            [eternal["lootName"]],
            eternal["count"],
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
        if item["lootItemType"] in ["WARDSKIN_RENTAL"]
    ]
    for skin in ward_skins:
        craft(
            ledge_token,
            ledge_url,
            puuid,
            "WARDSKIN_RENTAL_disenchant",
            [skin["lootName"]],
            skin["count"],
            proxy,
        )
