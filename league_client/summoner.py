def get_summoner_by_name(connection, name):
    res = connection.get(f"/lol-summoner/v1/summoners?name={name}")
    if not res.ok:
        return {"ok": False, "status_code": res.status_code, "detail": res.json()}
    return {"ok": True, "data": res.json()}


def get_current_summoner(connection):
    res = connection.get("/lol-summoner/v1/current-summoner")
    if not res.ok:
        return None
    return res.json()


def get_summoner_level(connection):
    data = get_current_summoner(connection)
    if data is None:
        return None
    return data["summonerLevel"] + data["percentCompleteForNextLevel"] / 100


def get_summoner_puuid(connection):
    data = get_current_summoner(connection)
    if data is None:
        return None
    return data["puuid"]


def get_summoner_id(connection):
    data = get_current_summoner(connection)
    if data is None:
        return None
    return data["summonerId"]
