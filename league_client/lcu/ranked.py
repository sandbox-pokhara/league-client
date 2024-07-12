from league_client.connection import LeagueConnection


def get_ranked_stats(connection: LeagueConnection):
    res = connection.get("/lol-ranked/v1/current-ranked-stats")
    res.raise_for_status()
    res = res.json()
    data = {
        "tier": res["queueMap"]["RANKED_SOLO_5x5"]["tier"],
        "division": res["queueMap"]["RANKED_SOLO_5x5"]["division"],
        "leaguePoints": res["queueMap"]["RANKED_SOLO_5x5"]["leaguePoints"],
        "wins": res["queueMap"]["RANKED_SOLO_5x5"]["wins"],
        "losses": res["queueMap"]["RANKED_SOLO_5x5"]["losses"],
    }
    return data
