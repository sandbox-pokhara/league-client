import re
import time
import uuid
from typing import Any

import httpx

from league_client.constants import HEADERS
from league_client.rso.loot import get_champion_mastery_chest_count
from league_client.rso.loot import get_generic_chest_count
from league_client.rso.loot import get_key_count
from league_client.rso.loot import get_key_fragment_count
from league_client.rso.loot import get_loot
from league_client.rso.loot import get_masterwork_chest_count
from league_client.rso.models import RSOSession


def craft(
    session: RSOSession,
    recipe_name: str,
    loot_names: list[str],
    repeat: int = 1,
):
    """Craft or open an chest item"""
    h = HEADERS.copy()
    h["Authorization"] = f"Bearer {session.ledge_token}"

    data = {
        "clientId": "LolClient-LEdge",
        "lootNameRefIds": [
            {"lootName": loot_name, "refId": ""} for loot_name in loot_names
        ],
        "recipeName": recipe_name,
        "repeat": repeat,
        "transactionId": str(uuid.uuid4()),
    }
    print(data)
    url = session.get_ledge_url(f"loot/v2/player/{session.puuid}/craft")
    res = httpx.post(
        url,
        headers=h,
        json=data,
        proxy=session.proxy,
    )
    res.raise_for_status()
    return res.json()


def craft_key_from_key_fragments(session: RSOSession, repeat: int = 1):
    return craft(
        session,
        "MATERIAL_key_fragment_forge",
        ["MATERIAL_key_fragment"],
        repeat,
    )


def craft_generic_chests(session: RSOSession, repeat: int = 1):
    craft(
        session,
        "CHEST_generic_OPEN",
        ["CHEST_generic", "MATERIAL_key"],
        repeat,
    )


def craft_champion_mastery_chest(session: RSOSession, repeat: int = 1):
    craft(
        session,
        "CHEST_champion_mastery_OPEN",
        ["CHEST_champion_mastery", "MATERIAL_key"],
        repeat,
    )


def craft_keys_and_generic_chests(session: RSOSession, retry_limit: int = 10):
    for _ in range(retry_limit):
        loot = get_loot(session)
        if loot == []:
            return

        forgable_keys = int(get_key_fragment_count(loot) / 3)
        key_count = get_key_count(loot)
        chest_count = get_generic_chest_count(loot)
        chest_count += get_champion_mastery_chest_count(loot)
        if (forgable_keys == 0 and key_count == 0) or chest_count == 0:
            return
        if forgable_keys > 0:
            craft_key_from_key_fragments(session, forgable_keys)
            continue

        if min(key_count, chest_count) > 0:
            craft_generic_chests(session)
            craft_champion_mastery_chest(session)


def craft_keys_and_masterwork_chests(
    session: RSOSession, retry_limit: int = 10
):
    for _ in range(retry_limit):
        loot = get_loot(session)
        if loot == []:
            return

        forgable_keys = int(get_key_fragment_count(loot) / 3)
        key_count = get_key_count(loot)
        chest_count = get_masterwork_chest_count(loot)

        if (forgable_keys == 0 and key_count == 0) or chest_count == 0:
            return
        if forgable_keys > 0:
            craft_key_from_key_fragments(session, forgable_keys)
            continue

        if min(key_count, chest_count) > 0:
            craft_generic_chests(session)
            craft_champion_mastery_chest(session)


def craft_chest_by_loot_id(
    session: RSOSession,
    loot_id: str,
    requires_key: bool = False,
    repeat: int = 1,
):
    """Craft or open an chest item by loot id"""
    loot_names = [loot_id]
    if requires_key:
        loot_names.append("MATERIAL_key")
    return craft(session, f"{loot_id}_OPEN", loot_names, repeat)


def craft_chest_loots(
    session: RSOSession,
    loots: list[dict[str, Any]],
    requires_key: bool = True,
):
    for loot in loots:
        count: int = loot["count"]
        if requires_key:
            key_count: int = get_key_count(loots)
            if key_count == 0:
                return
            count: int = min(count, key_count)
        craft_chest_by_loot_id(
            session, loot["lootName"], requires_key=requires_key, repeat=count
        )
        time.sleep(1)


def craft_champion_capsules(session: RSOSession):
    loot = get_loot(session)

    champion_capsules = [
        l
        for l in loot
        if re.fullmatch(
            "CHEST_((?!(generic|224|champion_mastery)).)*", l["lootName"]
        )
    ]
    craft_chest_loots(session, champion_capsules, requires_key=False)


def craft_mythic_essence_into_skin_shard(session: RSOSession):
    data = get_loot(session)
    loot_result = [m for m in data if m["lootName"] == "CURRENCY_mythic"]
    if loot_result == []:
        return
    count = loot_result[0]["count"]
    if count < 10:
        return
    return craft(
        session, "CURRENCY_mythic_forge_13", ["CURRENCY_mythic"], count // 10
    )
