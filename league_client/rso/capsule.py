import json
import time
from typing import Any
from typing import Optional

from httpx._types import ProxyTypes

from league_client.rso.craft import craft_by_name


def open_all_capsule(
    ledge_token: str,
    ledge_url: str,
    puuid: str,
    loot_data: dict[str, Any],
    proxy: Optional[ProxyTypes] = None,
):
    """
    This opens following capsules:-
        1. champion capsule
        2. ward shard capsule

    """
    # print(loot_data["playerLoot"])
    all_capsule = [
        item
        for item in loot_data["playerLoot"]
        if item["lootItemType"] == "CHEST"
    ]
    for capsule in all_capsule:
        recipe_name = f"{capsule['lootName']}_OPEN"
        response = craft_by_name(
            ledge_token,
            ledge_url,
            puuid,
            recipe_name,
            [capsule["lootName"]],
            1,
            proxy,
        )
        with open(f"{time.time()}.json", "w") as fp:
            json.dump(response, fp)
