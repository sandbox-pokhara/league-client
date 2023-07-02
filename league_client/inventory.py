import json

import requests


def get_inventory_by_type(connection, inventory_type):
    try:
        res = connection.get(f"/lol-inventory/v2/inventory/{inventory_type}")
        if not res.ok:
            return None
        return res.json()
    except (json.decoder.JSONDecodeError, requests.exceptions.RequestException):
        return None


def get_is_chroma(catalog, item_id):
    for i in catalog:
        if i["itemId"] == item_id:
            return i["subInventoryType"] == "RECOLOR"
    return False


def get_owned_skins(connection, filter_chroma=True):
    data = get_inventory_by_type(connection, "CHAMPION_SKIN")
    if data is None:
        return None
    data = [s["itemId"] for s in data if s["owned"]]
    if filter_chroma:
        res = connection.get("/lol-catalog/v1/items/CHAMPION_SKIN")
        if not res.ok:
            return None
        catalog = res.json()
        data = [i for i in data if not get_is_chroma(catalog, i)]
    return data
