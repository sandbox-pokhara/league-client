class LeagueClientError(Exception):
    pass


class RateLimitedError(LeagueClientError):
    pass


class RSOError(LeagueClientError):
    pass


class LCUError(LeagueClientError):
    pass


class AccountCheckError(RSOError):
    pass


class AuthFailureError(RSOError):
    pass


class AuthMultifactorError(AuthFailureError):
    pass


class InvalidSessionError(RSOError):
    pass


class AffnityDomainNotFound(RSOError):
    pass


class ChatHostNotFound(RSOError):
    pass


class LCUConnectionError(LCUError):
    pass


class AgeRestrictedError(LCUError):
    pass


class CountryRegionMissingError(LCUError):
    pass


class EmptyRQDataError(LCUError):
    pass


class LoginTokenError(LCUError):
    pass


class LCUAuthFailureError(LCUError):
    pass


class NeedsAuthenticationError(LCUError):
    pass


class ConsentRequiredError(LCUError):
    pass


class LCURateLimitedError(LCUError):
    pass


class LoginTimeoutError(LCUError):
    pass


class UnknownPhaseError(LCUError):
    pass


class RegionMissingError(LCUError):
    pass


class AccountBannedError(LCUError):
    pass


class NameChangeRequiredError(LCUError):
    pass


class VNGAccountError(LCUError):
    pass


class PatchTimeoutError(LCUError):
    pass


class WrongAccountLoggedInError(LCUError):
    pass
