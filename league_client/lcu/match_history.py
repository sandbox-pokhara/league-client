from typing import Any

from league_client.connection import LeagueConnection


def get_match_history(connection: LeagueConnection, puuid: str):
    res = connection.get(f"/lol-match-history/v1/products/lol/{puuid}/matches")
    res.raise_for_status()
    return res.json()


def get_participants(
    connection: LeagueConnection, puuid: str, summoner_id: str
):
    history = get_match_history(connection, puuid)
    data: list[dict[str, Any]] = []
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


def get_flash_key(connection: LeagueConnection, puuid: str, summoner_id: str):
    participants = get_participants(connection, puuid, summoner_id)
    d_count = 0
    f_count = 0
    for p in participants:
        if p["spell1Id"] == 4:
            d_count += 1
        if p["spell2Id"] == 4:
            f_count += 1
    return "d" if d_count > f_count else "f"
