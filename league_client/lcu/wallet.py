import httpx


def get_wallet(connection: httpx.Client):
    """
    This endpoint has been deprecated by riot games
    """
    try:
        res = connection.get("/lol-store/v1/wallet")
        res.raise_for_status()
        return res.json()
    except (httpx.HTTPStatusError, httpx.RequestError):
        return None
