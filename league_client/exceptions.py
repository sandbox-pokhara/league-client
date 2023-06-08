__all__ = [
    'LeagueClientError',    # Base exception for all exceptions raised by this library.

    # Specific exceptions
    'ParseError',
    'RSOAuthorizeError'
]


class LeagueClientError(Exception):
    '''Base exception for all exceptions raised by this library.'''

    def __init__(self, message=None, code=None):
        self.message = message
        self.code = code
        super().__init__(message)


class ParseError(LeagueClientError):
    '''Raised when an error occurs during parsing process.'''


class RSOAuthorizeError(LeagueClientError):
    '''Raised when an error occurs during RSO authorization process.'''


class LeagueEdgeError(LeagueClientError):
    '''Raised when an error occurs during league_edge authorization process.'''
