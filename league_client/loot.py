import json
import re

import requests

SKIN_SHARD_RE = 'CHAMPION_SKIN_RENTAL_[0-9]+'
SKIN_SHARD_PERMA_RE = 'CHAMPION_SKIN_[0-9]+'


def get_orange_essence(connection):
    try:
        res = connection.get('/lol-loot/v1/player-loot-map/')
        if not res.ok:
            return None
        res = res.json()
        return res['CURRENCY_cosmetic']['count']
    except (json.decoder.JSONDecodeError, requests.RequestException, KeyError):
        return None



def get_loot_by_pattern(connection, pattern):
    try:
        res = connection.get('/lol-loot/v1/player-loot-map/')
        if not res.ok:
            return None
        data = [s['storeItemId']
                for s in res.json().values()
                if re.fullmatch(pattern, s['lootId'])]
        return data
    except (json.decoder.JSONDecodeError, requests.exceptions.RequestException):
        return None


def get_skin_shards(connection):
    return get_loot_by_pattern(connection, SKIN_SHARD_RE)


def get_perma_skin_shards(connection):
    return get_loot_by_pattern(connection, SKIN_SHARD_PERMA_RE)
