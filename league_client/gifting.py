def get_giftable_friends(connection):
    res = connection.get('/lol-store/v1/giftablefriends')
    if res.ok:
        return res.json()
    return []
