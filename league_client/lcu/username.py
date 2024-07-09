from league_client.connection import LeagueConnection


def get_username(connection: LeagueConnection):
    res = connection.get("/lol-login/v1/login-platform-credentials")
    res.raise_for_status()
    return res.json().get("username")
