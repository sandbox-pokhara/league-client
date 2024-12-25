from league_client.connection import LeagueConnection


def get_lobby_data(connection: LeagueConnection):
    """Returns the lobby json"""
    res = connection.get("/lol-lobby/v2/lobby")
    res.raise_for_status()
    return res.json()


def get_lobby_members(connection: LeagueConnection):
    """Returns the lobby members json"""
    res = connection.get("/lol-lobby/v2/lobby/members")
    res.raise_for_status()
    return res.json()


def create_lobby(connection: LeagueConnection, queue_id: int):
    """Creates a lobby with the queue id given"""
    data = {"queueId": queue_id}
    if queue_id in [2000, 2010, 2020]:
        res = connection.post(
            "/lol-lobby/v2/matchmaking/quick-search", json=data
        )
        res.raise_for_status()
        return res.json()

    res = connection.post("/lol-lobby/v2/lobby", json=data)
    res.raise_for_status()
    return res.json()


def delete_lobby(connection: LeagueConnection):
    """Deletes the current lobby"""
    connection.delete("/lol-lobby/v2/lobby")


def get_lobby_invitations(connection: LeagueConnection):
    """Returns the lobby invitations json"""
    res = connection.get("/lol-lobby/v2/lobby/invitations")
    res.raise_for_status()
    return res.json()


def invite_summoners_by_id(
    connection: LeagueConnection, summoner_ids: list[int]
):
    """Invites summoners to the lobby by their summoner id"""
    data = [{"toSummonerId": id} for id in summoner_ids]
    res = connection.post("/lol-lobby/v2/lobby/invitations", json=data)
    res.raise_for_status()
    return res.json()


def get_received_invitations(connection: LeagueConnection):
    """Returns the received invitations json"""
    res = connection.get("/lol-lobby/v2/received-invitations")
    res.raise_for_status()
    return res.json()


def accept_invitation(connection: LeagueConnection, invitation_id: str):
    """Accepts an invitation by the invitation id"""
    res = connection.post(
        f"/lol-lobby/v2/received-invitations/{invitation_id}/accept"
    )
    res.raise_for_status()


def decline_invitation(connection: LeagueConnection, invitation_id: str):
    """Declines an invitation by the invitation id"""
    res = connection.post(
        f"/lol-lobby/v2/received-invitations/{invitation_id}/decline"
    )
    res.raise_for_status()
