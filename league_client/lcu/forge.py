import time
from typing import Any
from typing import Dict
from typing import List

import httpx

from league_client.lcu.loot import get_champion_mastery_chest_count
from league_client.lcu.loot import get_generic_chest_count
from league_client.lcu.loot import get_key_count
from league_client.lcu.loot import get_key_fragment_count
from league_client.lcu.loot import get_loot
from league_client.lcu.loot import get_masterwork_chest_count
from league_client.logger import logger


def forge(
    connection: httpx.Client,
    recipe: str,
    data: list[str],
    repeat: int = 1,
) -> None:
    if repeat == 0:
        return
    logger.info(f"Forging {recipe}, repeat: {repeat}")
    connection.post(
        f"/lol-loot/v1/recipes/{recipe}/craft?repeat={repeat}", json=data
    )


def forge_key_from_key_fragments(connection: httpx.Client, repeat: int = 1):
    forge(
        connection,
        "MATERIAL_key_fragment_forge",
        ["MATERIAL_key_fragment"],
        repeat,
    )


def open_generic_chests(connection: httpx.Client, repeat: int = 1):
    forge(
        connection,
        "CHEST_generic_OPEN",
        ["CHEST_generic", "MATERIAL_key"],
        repeat,
    )


def open_masterwork_chests(connection: httpx.Client, repeat: int = 1):
    forge(connection, "CHEST_224_OPEN", ["CHEST_224", "MATERIAL_key"], repeat)


def open_champion_mastery_chest(connection: httpx.Client, repeat: int = 1):
    forge(
        connection,
        "CHEST_champion_mastery_OPEN",
        ["CHEST_champion_mastery", "MATERIAL_key"],
        repeat,
    )


def open_chest_by_loot_id(
    connection: httpx.Client,
    loot_id: str,
    requires_key: bool = True,
    repeat: int = 1,
):
    data = [loot_id]
    if requires_key:
        data.append("MATERIAL_key")
    forge(connection, f"{loot_id}_OPEN", data, repeat)


def open_chest_loots(
    connection: httpx.Client,
    loots: List[Dict[str, Any]],
    requires_key: bool = True,
):
    for loot in loots:
        count: int = loot["count"]
        if requires_key:
            key_count: int = get_key_count(connection)
            if key_count == 0:
                return
            count: int = min(count, key_count)
        open_chest_by_loot_id(
            connection, loot["lootId"], requires_key=requires_key, repeat=count
        )
        time.sleep(1)


def forge_keys_and_open_generic_chests(
    connection: httpx.Client, retry_limit: int = 10
):
    for _ in range(retry_limit):
        loot = get_loot(connection)
        if loot == []:
            time.sleep(1)
            continue
        forgable_keys = int(get_key_fragment_count(connection) / 3)
        key_count = get_key_count(connection)
        chest_count = get_generic_chest_count(connection)
        chest_count += get_champion_mastery_chest_count(connection)
        if (forgable_keys == 0 and key_count == 0) or chest_count == 0:
            return
        if forgable_keys > 0:
            forge_key_from_key_fragments(connection, forgable_keys)
            continue
        if min(key_count, chest_count) > 0:
            open_generic_chests(connection)
            open_champion_mastery_chest(connection)


def forge_keys_and_open_masterwork_chests(
    connection: httpx.Client, retry_limit: int = 10
):
    for _ in range(retry_limit):
        loot = get_loot(connection)
        if loot == []:
            time.sleep(1)
            continue

        forgable_keys = int(get_key_fragment_count(connection) / 3)
        key_count = get_key_count(connection)
        chest_count = get_masterwork_chest_count(connection)

        if (forgable_keys == 0 and key_count == 0) or chest_count == 0:
            return
        if forgable_keys > 0:
            forge_key_from_key_fragments(connection, forgable_keys)
            continue
        if min(key_count, chest_count) > 0:
            open_masterwork_chests(connection)


def open_orbs(connection: httpx.Client, retry_limit: int = 10):
    for _ in range(retry_limit):
        loot = get_loot(connection)
        if loot == []:
            time.sleep(1)
            continue
        orbs = [l for l in loot if "orb" in l["localizedName"].lower()]
        open_chest_loots(connection, orbs, requires_key=False)


def open_bags(connection: httpx.Client, retry_limit: int = 10):
    for _ in range(retry_limit):
        loot = get_loot(connection)
        if loot == []:
            time.sleep(1)
            continue
        bags = [l for l in loot if "bag" in l["localizedName"].lower()]
        open_chest_loots(connection, bags, requires_key=False)


def open_eternals_capsules(connection: httpx.Client, retry_limit: int = 10):
    for _ in range(retry_limit):
        loot = get_loot(connection)
        if loot == []:
            time.sleep(1)
            continue
        eternals_capsules = [
            l
            for l in loot
            if "eternals" in l["localizedName"].lower()
            and "capsule" in l["localizedName"].lower()
        ]
        open_chest_loots(connection, eternals_capsules, requires_key=False)
