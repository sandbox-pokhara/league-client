from .chat import get_p2p_domain
from .chat import get_platform_id


def get_friend_requests(connection):
    res = connection.get(f"/lol-chat/v1/friend-requests")
    if not res.ok:
        return []
    return res.json()


def post_friend_request(connection, summoner_puuid):
    platform_id = get_platform_id(connection)
    domain = get_p2p_domain(connection, platform_id)
    pid = summoner_puuid + "@" + domain
    data = {"pid": pid}
    res = connection.post(f"/lol-chat/v1/friend-requests", json=data)
    return res.ok
