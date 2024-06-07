class LeagueClientError(Exception):
    pass


class AuthFailureError(LeagueClientError):
    pass


class InvalidSessionError(LeagueClientError):
    pass


class AffnityDomainNotFound(LeagueClientError):
    pass


class ChatHostNotFound(LeagueClientError):
    pass
