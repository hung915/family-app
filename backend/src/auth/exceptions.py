from src.auth.constants import ErrorCode
from src.exceptions import BadRequest, Unauthorized


class InvalidToken(Unauthorized):
    def __init__(self) -> None:
        super().__init__(detail=ErrorCode.INVALID_TOKEN)


class TokenExpired(Unauthorized):
    def __init__(self) -> None:
        super().__init__(detail=ErrorCode.TOKEN_EXPIRED)


class EmailNotAllowed(BadRequest):
    def __init__(self) -> None:
        super().__init__(detail=ErrorCode.EMAIL_NOT_ALLOWED)


class NotAuthenticated(Unauthorized):
    def __init__(self) -> None:
        super().__init__(detail=ErrorCode.NOT_AUTHENTICATED)
