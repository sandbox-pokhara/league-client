def get_region(riot_connection):
    res = riot_connection.get("/riotclient/region-locale")
    if not res.ok:
        None
    res = res.json()
    return res["region"]


def get_userinfo(riot_connection):
    res = riot_connection.get("/riot-client-auth/v1/userinfo")
    if not res.ok:
        return None
    return res.json()
