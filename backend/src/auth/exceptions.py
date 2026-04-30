from src.auth.constants import ErrorCode
from src.exceptions import BadRequestError, UnauthorizedError


class InvalidToken(UnauthorizedError):
    CODE = ErrorCode.INVALID_TOKEN
    MESSAGE = 'Invalid or expired link'


class TokenExpired(UnauthorizedError):
    CODE = ErrorCode.TOKEN_EXPIRED
    MESSAGE = 'Login link has expired, please request a new one'


class EmailNotAllowed(BadRequestError):
    CODE = ErrorCode.EMAIL_NOT_ALLOWED
    MESSAGE = 'This email is not registered in the family'


class NotAuthenticated(UnauthorizedError):
    CODE = ErrorCode.NOT_AUTHENTICATED
    MESSAGE = 'Please sign in to continue'
