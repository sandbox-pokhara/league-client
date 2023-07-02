import requests


def get_ranked_stats(connection):
    try:
        res = connection.get("/lol-ranked/v1/current-ranked-stats")
        if res.ok:
            res = res.json()
            data = {
                "tier": res["queueMap"]["RANKED_SOLO_5x5"]["tier"],
                "division": res["queueMap"]["RANKED_SOLO_5x5"]["division"],
                "leaguePoints": res["queueMap"]["RANKED_SOLO_5x5"]["leaguePoints"],
                "wins": res["queueMap"]["RANKED_SOLO_5x5"]["wins"],
                "losses": res["queueMap"]["RANKED_SOLO_5x5"]["losses"],
            }
            return data
        return None
    except (KeyError, requests.exceptions.RequestException):
        return None
