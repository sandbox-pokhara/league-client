def get_wallet(connection):
    """
    This endpoint has been deprecated by riot games
    """
    res = connection.get("/lol-store/v1/wallet")
    if res.ok:
        return res.json()
    return None
