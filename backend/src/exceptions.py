from typing import ClassVar

from fastapi import HTTPException, status


class AppError(HTTPException):
    """Base for all application exceptions.

    Subclasses declare CODE (machine-readable) and MESSAGE (human-readable).
    The exception handler in main.py serialises both into the response body.
    """

    STATUS_CODE: ClassVar[int]
    CODE: ClassVar[str]
    MESSAGE: ClassVar[str]

    def __init__(self) -> None:
        super().__init__(status_code=self.STATUS_CODE, detail=self.CODE)


class NotFoundError(AppError):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    CODE = 'NOT_FOUND'
    MESSAGE = 'Resource not found'


class BadRequestError(AppError):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    CODE = 'BAD_REQUEST'
    MESSAGE = 'Bad request'


class UnauthorizedError(AppError):
    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    CODE = 'UNAUTHORIZED'
    MESSAGE = 'Authentication required'

    def __init__(self) -> None:
        super().__init__()
        self.headers = {'WWW-Authenticate': 'Bearer'}


class ForbiddenError(AppError):
    STATUS_CODE = status.HTTP_403_FORBIDDEN
    CODE = 'FORBIDDEN'
    MESSAGE = 'Access denied'
