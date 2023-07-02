def get_token(connection):
    res = connection.get("/entitlements/v1/token")
    if res.ok:
        return res.json()["accessToken"]
    return None
