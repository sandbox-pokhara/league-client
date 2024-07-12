from typing import Any
from typing import Optional

from httpx._types import ProxyTypes

from league_client.rso.constants import LootNameTypes
from league_client.rso.craft import craft


def open_champion_capsule(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    loot_data: dict[str, Any],
    proxy: Optional[ProxyTypes] = None,
):
    champion_capsule = [
        item for item in loot_data["playerLoot"] if item["type"] == "CHEST"
    ]
    for capsule in champion_capsule:
        recipe_name = f"{capsule['lootName']}_OPEN"
        craft(
            ledge_token,
            ledge_url,
            puuid,
            recipe_name,
            [LootNameTypes(capsule["lootName"])],
            1,
            proxy,
        )
