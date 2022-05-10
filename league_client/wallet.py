def get_wallet(connection):
    res = connection.get('/lol-store/v1/wallet')
    if res.ok:
        return res.json()
    return None
