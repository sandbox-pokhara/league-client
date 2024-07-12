from league_client.connection import LeagueConnection


def get_wallet(connection: LeagueConnection):
    res = connection.get("/lol-store/v1/wallet")
    res.raise_for_status()
    return res.json()
