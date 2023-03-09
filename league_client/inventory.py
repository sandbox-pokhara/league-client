import json

import requests


def get_inventory_by_type(connection, inventory_type):
    try:
        res = connection.get(f'/lol-inventory/v2/inventory/{inventory_type}')
        if not res.ok:
            return None
        return res.json()
    except (json.decoder.JSONDecodeError, requests.exceptions.RequestException):
        return None


def get_owned_skins(connection):
    data = get_inventory_by_type(connection, 'CHAMPION_SKIN')
    if data is None:
        return None
    data = [s['itemId'] for s in data if s['owned']]
    return data
