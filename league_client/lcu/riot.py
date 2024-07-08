import httpx


def get_region(riot_connection: httpx.Client):
    try:
        res = riot_connection.get("/riotclient/region-locale")
        res.raise_for_status()
        res = res.json()
        return res["region"]
    except (httpx.HTTPStatusError, httpx.RequestError):
        return None


def get_userinfo(riot_connection: httpx.Client):
    try:
        res = riot_connection.get("/riot-client-auth/v1/userinfo")
        res.raise_for_status()
        return res.json()
    except (httpx.HTTPStatusError, httpx.RequestError):
        return None
