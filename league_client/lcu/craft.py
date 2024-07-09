import re
import time
from typing import Any

from league_client.connection import LeagueConnection
from league_client.lcu.loot import get_champion_mastery_chest_count
from league_client.lcu.loot import get_generic_chest_count
from league_client.lcu.loot import get_key_count
from league_client.lcu.loot import get_key_fragment_count
from league_client.lcu.loot import get_loot
from league_client.lcu.loot import get_masterwork_chest_count


def craft(
    connection: LeagueConnection, recipe: str, data: list[str], repeat: int = 1
):
    connection.post(
        f"/lol-loot/v1/recipes/{recipe}/craft?repeat={repeat}", json=data
    )


def craft_key_from_key_fragments(
    connection: LeagueConnection, repeat: int = 1
):
    craft(
        connection,
        "MATERIAL_key_fragment_forge",
        ["MATERIAL_key_fragment"],
        repeat,
    )


def craft_keys_and_generic_chests(
    connection: LeagueConnection, retry_limit: int = 10
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
            craft_key_from_key_fragments(connection, forgable_keys)
            continue
        if min(key_count, chest_count) > 0:
            craft_generic_chests(connection)
            craft_champion_mastery_chest(connection)


def craft_keys_and_masterwork_chests(
    connection: LeagueConnection, retry_limit: int = 10
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
            craft_key_from_key_fragments(connection, forgable_keys)
            continue
        if min(key_count, chest_count) > 0:
            craft_masterwork_chests(connection)


def craft_mythic_essence_into_skin_shard(connection: LeagueConnection):
    data = get_loot(connection)
    loot_result = [m for m in data if m["lootId"] == "CURRENCY_mythic"]
    if loot_result == []:
        return
    for loot in loot_result:
        if loot["count"] < 10:
            return
        url = f'/lol-loot/v1/recipes/CURRENCY_mythic_forge_13/craft?repeat={loot["count"]//10}'
        data = [loot["lootName"]]
        connection.post(url, json=data)


def craft_generic_chests(connection: LeagueConnection, repeat: int = 1):
    craft(
        connection,
        "CHEST_generic_OPEN",
        ["CHEST_generic", "MATERIAL_key"],
        repeat,
    )


def craft_masterwork_chests(connection: LeagueConnection, repeat: int = 1):
    craft(connection, "CHEST_224_OPEN", ["CHEST_224", "MATERIAL_key"], repeat)


def craft_champion_mastery_chest(
    connection: LeagueConnection, repeat: int = 1
):
    craft(
        connection,
        "CHEST_champion_mastery_OPEN",
        ["CHEST_champion_mastery", "MATERIAL_key"],
        repeat,
    )


def craft_chest_by_loot_id(
    connection: LeagueConnection,
    loot_id: str,
    requires_key: bool = True,
    repeat: int = 1,
):
    data = [loot_id]
    if requires_key:
        data.append("MATERIAL_key")
    craft(connection, f"{loot_id}_OPEN", data, repeat)


def craft_chest_loots(
    connection: LeagueConnection,
    loots: list[dict[str, Any]],
    requires_key: bool = True,
):
    for loot in loots:
        count: int = loot["count"]
        if requires_key:
            key_count: int = get_key_count(connection)
            if key_count == 0:
                return
            count: int = min(count, key_count)
        craft_chest_by_loot_id(
            connection, loot["lootId"], requires_key=requires_key, repeat=count
        )
        time.sleep(1)


def craft_orbs(connection: LeagueConnection, retry_limit: int = 10):
    for _ in range(retry_limit):
        loot = get_loot(connection)
        if loot == []:
            time.sleep(1)
            continue
        orbs = [l for l in loot if "orb" in l["localizedName"].lower()]
        craft_chest_loots(connection, orbs, requires_key=False)


def craft_bags(connection: LeagueConnection, retry_limit: int = 10):
    for _ in range(retry_limit):
        loot = get_loot(connection)
        if loot == []:
            time.sleep(1)
            continue
        bags = [l for l in loot if "bag" in l["localizedName"].lower()]
        craft_chest_loots(connection, bags, requires_key=False)


def craft_eternals_capsules(
    connection: LeagueConnection, retry_limit: int = 10
):
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
        craft_chest_loots(connection, eternals_capsules, requires_key=False)


def craft_champion_capsules(connection: LeagueConnection):
    data = get_loot(connection)
    data = [
        m
        for m in data
        if re.fullmatch(
            "CHEST_((?!(generic|224|champion_mastery)).)*", m["lootId"]
        )
    ]
    if data == []:
        return

    for loot in data:
        url = "/lol-loot/v1/recipes/%s_OPEN/craft?repeat=%d" % (
            loot["lootName"],
            loot["count"],
        )
        data = [loot["lootName"]]
        connection.post(url, json=data)
