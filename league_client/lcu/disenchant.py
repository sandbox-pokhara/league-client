import json

import httpx

from league_client.lcu.loot import get_eternals
from league_client.lcu.loot import get_loot_name
from league_client.lcu.loot import get_ward_skins
from league_client.logger import logger


def get_disenchant_recipe(connection: httpx.Client, loot_id: str):
    try:
        res = connection.get(f"/lol-loot/v1/recipes/initial-item/{loot_id}")
        res.raise_for_status()
        recipes = [r for r in res.json() if r["type"] == "DISENCHANT"]
        if recipes == []:
            return None
        return recipes[0]
    except (
        httpx.HTTPStatusError,
        httpx.RequestError,
        json.JSONDecodeError,
        KeyError,
    ):
        return None


def disenchant(connection: httpx.Client, loot):
    for data in loot:
        name = get_loot_name(data)
        recipe = get_disenchant_recipe(connection, data["lootId"])
        if recipe is None:
            logger.info(f"No disenchant recipe found for {name}.")
            continue
        logger.info(
            f"Disenchanting: {name}, "
            f"Count: {data['count']}, "
            f"Value: {data['disenchantValue']}"
        )
        url = f'/lol-loot/v1/recipes/{recipe["recipeName"]}/craft?repeat={data["count"]}'
        data = [data["lootName"]]
        try:
            res = connection.post(url, json=data)
            res.raise_for_status()
            logger.info("Disenchanting successful.")
        except (
            httpx.HTTPStatusError,
            httpx.RequestError,
            json.JSONDecodeError,
            KeyError,
        ):
            logger.info("Disenchanting unsuccessful. Something went wrong!")


def disenchant_eternals(connection: httpx.Client):
    data = get_eternals(connection)
    return disenchant(connection, data)


def disenchant_ward_skins(connection: httpx.Client):
    data = get_ward_skins(connection)
    return disenchant(connection, data)
