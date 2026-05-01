from src.exceptions import NotFoundError
from src.members.constants import ErrorCode


class MemberNotFound(NotFoundError):  # noqa: N818
    CODE = ErrorCode.MEMBER_NOT_FOUND
    MESSAGE = 'Member not found'


class MemberAlreadyExists(NotFoundError):  # noqa: N818
    CODE = ErrorCode.MEMBER_ALREADY_EXISTS
    MESSAGE = 'A member with this email already exists'
