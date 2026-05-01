from src.auth.constants import ErrorCode
from src.exceptions import UnauthorizedError


class InvalidCredentials(UnauthorizedError):  # noqa: N818
    CODE = ErrorCode.INVALID_CREDENTIALS
    MESSAGE = 'Invalid email or password'


class InvalidToken(UnauthorizedError):  # noqa: N818
    CODE = ErrorCode.INVALID_TOKEN
    MESSAGE = 'Invalid or expired session'


class NotAuthenticated(UnauthorizedError):  # noqa: N818
    CODE = ErrorCode.NOT_AUTHENTICATED
    MESSAGE = 'Please sign in to continue'
