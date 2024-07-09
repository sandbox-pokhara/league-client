from league_client.connection import LeagueConnection


def get_summoner_by_name(connection: LeagueConnection, name: str):
    res = connection.get(f"/lol-summoner/v1/summoners?name={name}")
    res.raise_for_status()
    return res.json()


def get_current_summoner(connection: LeagueConnection):
    res = connection.get("/lol-summoner/v1/current-summoner")
    res.raise_for_status()
    return res.json()


def get_summoner_level(connection: LeagueConnection):
    data = get_current_summoner(connection)
    return data["summonerLevel"] + data["percentCompleteForNextLevel"] / 100


def get_summoner_puuid(connection: LeagueConnection):
    data = get_current_summoner(connection)
    return data["puuid"]


def get_summoner_id(connection: LeagueConnection):
    data = get_current_summoner(connection)
    return data["summonerId"]
