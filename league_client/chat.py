def get_platform_id(connection):
    res = connection.get("/lol-chat/v1/me")
    if res.ok:
        res = res.json()
        return res["platformId"]
    return None


def get_p2p_domain(connection, platform_id):
    res = connection.get("/lol-chat/v1/config")
    if res.ok:
        res = res.json()
        domain = res["ChatDomain"]["P2PDomainName"]
        region = res["LcuSocial"]["platformToRegionMap"][platform_id]
        return region + "." + domain
    return None
