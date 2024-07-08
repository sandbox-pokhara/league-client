import json
from typing import Dict
from typing import List

import httpx


def get_inventory_by_type(connection: httpx.Client, inventory_type: str):
    try:
        res = connection.get(f"/lol-inventory/v2/inventory/{inventory_type}")
        res.raise_for_status()
        return res.json()
    except (
        httpx.HTTPStatusError,
        httpx.RequestError,
        json.JSONDecodeError,
        KeyError,
    ):
        return None


def get_is_chroma(catalog: List[Dict[str, str]], item_id: str) -> bool:
    for i in catalog:
        if i["itemId"] == item_id:
            return i["subInventoryType"] == "RECOLOR"
    return False


def get_owned_skins(connection: httpx.Client, filter_chroma: bool = True):
    data = get_inventory_by_type(connection, "CHAMPION_SKIN")
    if data is None:
        return None
    data = [s["itemId"] for s in data if s["owned"]]
    try:
        if filter_chroma:
            res = connection.get("/lol-catalog/v1/items/CHAMPION_SKIN")
            res.raise_for_status()
            catalog = res.json()
            data = [i for i in data if not get_is_chroma(catalog, i)]
        return data
    except (
        httpx.HTTPStatusError,
        httpx.RequestError,
        json.JSONDecodeError,
        KeyError,
    ):
        return None
