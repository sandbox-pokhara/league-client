from typing import Any
from typing import Optional

from httpx._types import ProxyTypes

from league_client.rso.craft import craft_by_name


def forge_keys(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    loot_data: dict[str, Any],
    proxy: Optional[ProxyTypes] = None,
):
    keys = [
        item
        for item in loot_data["playerLoot"]
        if item["lootName"] == "MATERIAL_key_fragment"
    ]
    for key in keys:
        recipe_name = f"{key['lootName']}_forge"
        # requires 3 keys fragment to form one key
        if key["count"] < 3:
            continue
        repeat = key["count"] // 3
        craft_by_name(
            ledge_token,
            ledge_url,
            puuid,
            recipe_name,
            [key["lootName"]],
            repeat,
            proxy,
        )
