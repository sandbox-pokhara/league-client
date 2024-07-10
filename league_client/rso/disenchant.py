from league_client.rso.craft import craft
from league_client.rso.loot import get_loot
from league_client.rso.models import RSOSession


def disenchant_champion_shards(session: RSOSession):
    loot = get_loot(session)
    champion_shards = [
        l for l in loot if l["type"] in ["CHAMPION", "CHAMPION_RENTAL"]
    ]
    for shard in champion_shards:
        recipe_name = f"{shard['type'].split('_')[0]}_disenchant"
        craft(
            session,
            recipe_name,
            [shard["lootName"]],
        )


def disenchant_eternals(session: RSOSession):
    loot = get_loot(session)
    eternals = [l for l in loot if l["type"] == "STATSTONE_SHARD"]
    for eternal in eternals:
        recipe_name = f"STATSTONE_SHARD_DISENCHANT"
        craft(
            session,
            recipe_name,
            [eternal["lootName"]],
        )


def disenchant_ward_skins(session: RSOSession):
    loot = get_loot(session)
    ward_skins = [l for l in loot if l["type"] == "STATSTONE_SHARD"]
    for skin in ward_skins:
        recipe_name = f"WARDSKIN_disenchant"
        craft(
            session,
            recipe_name,
            [skin["lootName"]],
        )
