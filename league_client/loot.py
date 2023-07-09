import json
import re

import requests

SKIN_SHARD_RE = "CHAMPION_SKIN_RENTAL_[0-9]+"
SKIN_SHARD_PERMA_RE = "CHAMPION_SKIN_[0-9]+"


def get_loot(connection):
    res = connection.get("/lol-loot/v1/player-loot")
    if not res.ok:
        return []
    return res.json()


def get_player_loot_map(connection):
    res = connection.get("/lol-loot/v1/player-loot-map/")
    if not res.ok:
        return {}
    return res.json()


def get_loot_count(connection, loot_id):
    loot = get_loot(connection)
    if loot == []:
        return -1
    filtered_loot = [l for l in loot if l["lootId"] == loot_id]
    if filtered_loot == []:
        return 0
    return filtered_loot[0]["count"]


def get_loot_by_id(connection, loot_id):
    res = connection.get(f"/lol-loot/v1/player-loot/{loot_id}")
    if not res.ok:
        return []
    return res.json()


def get_loot_name(loot):
    if loot["localizedName"] != "":
        return loot["localizedName"]
    if loot["itemDesc"] != "":
        return loot["itemDesc"]
    return loot["lootId"]


def get_loot_by_pattern(connection, pattern):
    try:
        res = connection.get("/lol-loot/v1/player-loot-map/")
        if not res.ok:
            return None
        data = [
            s["storeItemId"]
            for s in res.json().values()
            if re.fullmatch(pattern, s["lootId"])
        ]
        return data
    except (json.decoder.JSONDecodeError, requests.exceptions.RequestException):
        return None


def get_eternals(connection):
    loot = get_loot(connection)
    return [l for l in loot if l["type"] == "STATSTONE_SHARD"]


def get_ward_skins(connection):
    loot = get_loot(connection)
    return [l for l in loot if l["type"].startswith("WARDSKIN_")]


def get_orange_essence(connection):
    try:
        res = connection.get("/lol-loot/v1/player-loot-map/")
        if not res.ok:
            return None
        res = res.json()
        if "CURRENCY_cosmetic" not in res:
            return 0
        return res["CURRENCY_cosmetic"]["count"]
    except (json.decoder.JSONDecodeError, requests.RequestException, KeyError):
        return None


def get_skin_shards(connection):
    return get_loot_by_pattern(connection, SKIN_SHARD_RE)


def get_perma_skin_shards(connection):
    return get_loot_by_pattern(connection, SKIN_SHARD_PERMA_RE)


def get_key_fragment_count(connection):
    return get_loot_count(connection, "MATERIAL_key_fragment")


def get_key_count(connection):
    return get_loot_count(connection, "MATERIAL_key")


def get_generic_chest_count(connection):
    return get_loot_count(connection, "CHEST_generic")


def get_champion_mastery_chest_count(connection):
    return get_loot_count(connection, "CHEST_champion_mastery")


def get_masterwork_chest_count(connection):
    return get_loot_count(connection, "CHEST_224")


def get_blue_essence_count(connection):
    return get_loot_count(connection, "CURRENCY_champion")
