from aiohttp import ContentTypeError

__all__ = [
    "LeagueClientError",  # Base exception for all exceptions raised by this library.
    # Specific exceptions
    "ParseError",
    "RSOAuthorizeError",
]


class LeagueClientError(Exception):
    """Base exception for all exceptions raised by this library."""

    def __init__(self, message=None, code=None):
        self.message = message
        self.code = code
        super().__init__(message)


class RegionNotSupportedError(LeagueClientError):
    def __init__(self, message, code, region):
        self.region = region
        super().__init__(message, code)


class SummonerNotFoundError(LeagueClientError):
    """Raised when an account does not have summoner (level 1 account with no summoner name)."""

    def __init__(self, message, code, region):
        # can be used as fresh accounts
        # so region data is required
        self.region = region
        super().__init__(message, code)


class ParseError(LeagueClientError):
    """Raised when an error occurs during parsing process."""


class RSOAuthorizeError(LeagueClientError):
    """Raised when an error occurs during RSO authorization process."""


class LeagueEdgeError(LeagueClientError):
    """Raised when an error occurs during league_edge authorization process."""


class LeagueEdgeBadResponse(LeagueEdgeError):
    """Raised when res.ok is false during league_edge authorization process."""

    def __init__(self, message, code, status_code, json_):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.json = json_
        super().__init__(message, code)

    @classmethod
    async def create(self, message, code, res):
        try:
            data = await res.json()
        except ContentTypeError:
            data = None
        return LeagueEdgeBadResponse(message, code, res.status, data)


class AccountRestrictedError(LeagueClientError):
    """Raised when an account has one or more restrictions"""


class AccountBannedError(AccountRestrictedError):
    """Raised when an account has been permanently banned"""


class ChatRestrictedError(AccountRestrictedError):
    """Raised when an account has been chat restricted"""


class TimeBanError(AccountRestrictedError):
    """Raised when an account has TIME_BAN restriction"""


class ConnectedAccountsError(LeagueClientError):
    """Raised when an account has other connected accounts"""


class RiotUserInfoError(LeagueClientError):
    """Raised when an error occurs during GET riot user info."""
