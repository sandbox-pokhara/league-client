from typing import Any
from typing import Optional

from httpx._types import ProxyTypes

from league_client.rso.constants import LootNameTypes
from league_client.rso.craft import craft


def forge_keys(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    loot_data: dict[str, Any],
    proxy: Optional[ProxyTypes] = None,
):
    orbs = [
        item
        for item in loot_data["playerLoot"]
        if item["lootName"] == "MATERIAL_key_fragment"
    ]
    for orb in orbs:
        recipe_name = f"{orb['lootName']}_forge"
        # requires 3 keys fragment to form one key
        if orb["count"] < 3:
            continue
        repeat = orb["count"] // 3
        craft(
            ledge_token,
            ledge_url,
            puuid,
            recipe_name,
            [LootNameTypes(orb["lootName"])],
            repeat,
            proxy,
        )
