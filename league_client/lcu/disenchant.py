from typing import Any

from league_client.connection import LeagueConnection
from league_client.lcu.loot import get_champion_shards
from league_client.lcu.loot import get_eternals
from league_client.lcu.loot import get_ward_skins


def get_disenchant_recipe(connection: LeagueConnection, loot_id: str):
    res = connection.get(f"/lol-loot/v1/recipes/initial-item/{loot_id}")
    res.raise_for_status()
    recipes = [r for r in res.json() if r["type"] == "DISENCHANT"]
    return recipes[0]


def disenchant(connection: LeagueConnection, loot: Any):
    for data in loot:
        recipe = get_disenchant_recipe(connection, data["lootId"])
        url = f'/lol-loot/v1/recipes/{recipe["recipeName"]}/craft?repeat={data["count"]}'
        data = [data["lootName"]]
        res = connection.post(url, json=data)
        res.raise_for_status()


def disenchant_eternals(connection: LeagueConnection):
    data = get_eternals(connection)
    return disenchant(connection, data)


def disenchant_ward_skins(connection: LeagueConnection):
    data = get_ward_skins(connection)
    return disenchant(connection, data)


def disenchant_champion_shards(connection: LeagueConnection):
    data = get_champion_shards(connection)
    return disenchant(connection, data)
