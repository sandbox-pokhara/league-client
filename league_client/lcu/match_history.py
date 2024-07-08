from typing import Any
from typing import Dict
from typing import List

import httpx

from league_client.logger import logger


def get_match_history(connection: httpx.Client, puuid: str):
    try:
        res = connection.get(
            f"/lol-match-history/v1/products/lol/{puuid}/matches"
        )
        res.raise_for_status()
        return res.json()
    except (httpx.HTTPStatusError, httpx.RequestError, Exception):
        logger.error(f"HTTP error occurred during disenchanting")
        return None


def get_participants(
    connection: httpx.Client, puuid: str, summoner_id: str
) -> List[Dict[str, Any]]:
    history = get_match_history(connection, puuid)
    if history is None:
        return []
    data: List[Dict[str, Any]] = []
    for game in history["games"]["games"]:
        pid = None
        for p in game["participantIdentities"]:
            if p["player"]["summonerId"] == summoner_id:
                pid = p["participantId"]
                break
        if pid is None:
            continue
        for p in game["participants"]:
            if p["participantId"] == pid:
                data.append(p)
    return data


def get_flash_key(connection: httpx.Client, puuid: str, summoner_id: str):
    participants = get_participants(connection, puuid, summoner_id)
    d_count = 0
    f_count = 0
    for p in participants:
        if p["spell1Id"] == 4:
            d_count += 1
        if p["spell2Id"] == 4:
            f_count += 1
    return "d" if d_count > f_count else "f"
