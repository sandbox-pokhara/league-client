import re

from league_client.connection import LeagueConnection

SKIN_SHARD_RE = "CHAMPION_SKIN_RENTAL_[0-9]+"
SKIN_SHARD_PERMA_RE = "CHAMPION_SKIN_[0-9]+"


def get_loot(connection: LeagueConnection):
    res = connection.get("/lol-loot/v1/player-loot")
    res.raise_for_status()
    return res.json()


def get_player_loot_map(connection: LeagueConnection):
    res = connection.get("/lol-loot/v1/player-loot-map")
    res.raise_for_status()
    return res.json()


def get_loot_count(connection: LeagueConnection, loot_id: str) -> int:
    loot = get_loot(connection)
    filtered_loot = [l for l in loot if l["lootId"] == loot_id]
    if filtered_loot == []:
        return 0
    return filtered_loot[0]["count"]


def get_loot_by_id(connection: LeagueConnection, loot_id: str):
    res = connection.get(f"/lol-loot/v1/player-loot/{loot_id}")
    res.raise_for_status()
    return res.json()


def get_loot_by_pattern(connection: LeagueConnection, pattern: str):
    res = connection.get("/lol-loot/v1/player-loot-map")
    res.raise_for_status()
    data = [
        s for s in res.json().values() if re.fullmatch(pattern, s["lootId"])
    ]
    return data


def get_eternals(connection: LeagueConnection):
    loot = get_loot(connection)
    return [l for l in loot if l["type"] == "STATSTONE_SHARD"]


def get_ward_skins(connection: LeagueConnection):
    loot = get_loot(connection)
    return [l for l in loot if l["type"].startswith("WARDSKIN_")]


def get_champion_shards(connection: LeagueConnection):
    loot = get_loot(connection)
    return [l for l in loot if l["type"] in ["CHAMPION", "CHAMPION_RENTAL"]]


def get_skin_shards(connection: LeagueConnection):
    return get_loot_by_pattern(connection, SKIN_SHARD_RE)


def get_perma_skin_shards(connection: LeagueConnection):
    return get_loot_by_pattern(connection, SKIN_SHARD_PERMA_RE)


def get_skin_shards_ids(connection: LeagueConnection):
    return [s["storeItemId"] for s in get_skin_shards(connection)]


def get_perma_skin_shards_ids(connection: LeagueConnection):
    return [s["storeItemId"] for s in get_perma_skin_shards(connection)]


def get_key_fragment_count(connection: LeagueConnection) -> int:
    return get_loot_count(connection, "MATERIAL_key_fragment")


def get_key_count(connection: LeagueConnection) -> int:
    return get_loot_count(connection, "MATERIAL_key")


def get_generic_chest_count(connection: LeagueConnection) -> int:
    return get_loot_count(connection, "CHEST_generic")


def get_champion_mastery_chest_count(connection: LeagueConnection) -> int:
    return get_loot_count(connection, "CHEST_champion_mastery")


def get_masterwork_chest_count(connection: LeagueConnection) -> int:
    return get_loot_count(connection, "CHEST_224")


def get_blue_essence_count(connection: LeagueConnection) -> int:
    return get_loot_count(connection, "CURRENCY_champion")


def get_orange_essence_count(connection: LeagueConnection):
    return get_loot_count(connection, "CURRENCY_cosmetic")
