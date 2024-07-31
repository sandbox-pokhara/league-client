from typing import Any


def extract_skin_id(loot_name: str, loot_text: str) -> int:
    skin_id = loot_name.split(loot_text)[1]
    if "_" in skin_id:
        skin_id = skin_id.split("_")[1]
        return int(skin_id)
    return int(skin_id)


def get_skins(
    champion_skin_inventory_data: dict[str, Any], loot_data: dict[str, Any]
):
    # return tuple of owned, normal, permanent skin ids
    owned_skins: list[int] = champion_skin_inventory_data["items"][
        "CHAMPION_SKIN"
    ]

    player_loot: list[dict[str, Any]] = loot_data["playerLoot"]
    all_skins: list[str] = [
        item["lootName"]
        for item in list(
            filter(
                lambda item: "CHAMPION_SKIN_" in item["lootName"], player_loot
            )
        )
    ]
    normal_skins = list(
        filter(lambda item: "CHAMPION_SKIN_RENTAL" in item, all_skins)
    )
    perma_skins = list(
        filter(lambda item: item not in normal_skins, all_skins)
    )
    if normal_skins:
        normal_skins = [
            extract_skin_id(item, "CHAMPION_SKIN_RENTAL")
            for item in normal_skins
        ]
    if perma_skins:
        perma_skins = [
            extract_skin_id(item, "CHAMPION_SKIN") for item in perma_skins
        ]
    return owned_skins, normal_skins, perma_skins
