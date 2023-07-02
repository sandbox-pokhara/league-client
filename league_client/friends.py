def get_friend_exists(connection, summoner_id):
    res = connection.get(f"/lol-chat/v1/friend-exists/{summoner_id}")
    if not res.ok:
        return False
    return res.json()
