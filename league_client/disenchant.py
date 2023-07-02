from .logger import logger
from .loot import get_eternals
from .loot import get_loot_name
from .loot import get_ward_skins


def get_disenchant_recipe(connection, loot_id):
    res = connection.get(f"/lol-loot/v1/recipes/initial-item/{loot_id}")
    if not res.ok:
        return None
    recipes = [r for r in res.json() if r["type"] == "DISENCHANT"]
    if recipes == []:
        return None
    return recipes[0]


def disenchant(connection, loot):
    for data in loot:
        name = get_loot_name(data)
        recipe = get_disenchant_recipe(connection, data["lootId"])
        if recipe is None:
            logger.info(f"No disenchant recipe found for {name}.")
            continue
        logger.info(
            f"Disenchanting: {name}, "
            f'Count: {data["count"]}, '
            f'Value: {data["disenchantValue"]}'
        )
        url = (
            f'/lol-loot/v1/recipes/{recipe["recipeName"]}/craft?repeat={data["count"]}'
        )
        data = [data["lootName"]]
        res = connection.post(url, json=data)
        if res.ok:
            logger.info("Success.")
        else:
            logger.info("Failed.")
            logger.debug(res.text)


def disenchant_eternals(connection):
    data = get_eternals(connection)
    return disenchant(connection, data)


def disenchant_ward_skins(connection):
    data = get_ward_skins(connection)
    return disenchant(connection, data)
