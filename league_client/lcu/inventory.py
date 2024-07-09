from league_client.connection import LeagueConnection


def get_inventory_by_type(connection: LeagueConnection, inventory_type: str):
    res = connection.get(f"/lol-inventory/v2/inventory/{inventory_type}")
    res.raise_for_status()
    return res.json()


def get_is_chroma(catalog: list[dict[str, str]], item_id: str):
    for i in catalog:
        if i["itemId"] == item_id:
            return i["subInventoryType"] == "RECOLOR"
    return False


def get_owned_skins(connection: LeagueConnection, filter_chroma: bool = True):
    data = get_inventory_by_type(connection, "CHAMPION_SKIN")
    if data is None:
        return None
    data = [s["itemId"] for s in data if s["owned"]]
    if filter_chroma:
        res = connection.get("/lol-catalog/v1/items/CHAMPION_SKIN")
        res.raise_for_status()
        catalog = res.json()
        data = [i for i in data if not get_is_chroma(catalog, i)]
    return data
