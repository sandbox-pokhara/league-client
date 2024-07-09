from league_client.connection import LeagueConnection


def get_userinfo(riot_connection: LeagueConnection):
    res = riot_connection.get("/riot-client-auth/v1/userinfo")
    res.raise_for_status()
    return res.json()
