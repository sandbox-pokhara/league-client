from league_client.connection import LeagueConnection


def get_region(riot_connection: LeagueConnection):
    res = riot_connection.get("/riotclient/region-locale")
    res.raise_for_status()
    res = res.json()
    return res["region"]
