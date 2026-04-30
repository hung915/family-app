from src.auth.constants import ErrorCode
from src.exceptions import BadRequest, Unauthorized


class InvalidToken(Unauthorized):
    CODE = ErrorCode.INVALID_TOKEN
    MESSAGE = 'Invalid or expired link'


class TokenExpired(Unauthorized):
    CODE = ErrorCode.TOKEN_EXPIRED
    MESSAGE = 'Login link has expired, please request a new one'


class EmailNotAllowed(BadRequest):
    CODE = ErrorCode.EMAIL_NOT_ALLOWED
    MESSAGE = 'This email is not registered in the family'


class NotAuthenticated(Unauthorized):
    CODE = ErrorCode.NOT_AUTHENTICATED
    MESSAGE = 'Please sign in to continue'
