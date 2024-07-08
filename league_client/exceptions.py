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


class ParseError(LeagueClientError):
    """Raised when an error occurs during parsing process."""


class RSOAuthorizeError(LeagueClientError):
    """Raised when an error occurs during RSO authorization process."""
