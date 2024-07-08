import httpx


def get_summoner_by_name(connection: httpx.Client, name: str):
    try:
        res = connection.get(f"/lol-summoner/v1/summoners?name={name}")
        res.raise_for_status()
        return {"ok": True, "data": res.json()}
    except httpx.HTTPStatusError as exc:
        return {
            "ok": False,
            "status_code": exc.response.status_code,
            "detail": exc.response.json(),
        }


def get_current_summoner(connection: httpx.Client):
    try:
        res = connection.get("/lol-summoner/v1/current-summoner")
        res.raise_for_status()
        return res.json()
    except (httpx.HTTPStatusError, httpx.RequestError):
        return None


def get_summoner_level(connection: httpx.Client):
    data = get_current_summoner(connection)
    if data is None:
        return None
    return data["summonerLevel"] + data["percentCompleteForNextLevel"] / 100


def get_summoner_puuid(connection: httpx.Client):
    data = get_current_summoner(connection)
    if data is None:
        return None
    return data["puuid"]


def get_summoner_id(connection: httpx.Client):
    data = get_current_summoner(connection)
    if data is None:
        return None
    return data["summonerId"]
