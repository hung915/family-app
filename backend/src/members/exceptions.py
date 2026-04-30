from src.exceptions import NotFound
from src.members.constants import ErrorCode


class MemberNotFound(NotFound):
    CODE = ErrorCode.MEMBER_NOT_FOUND
    MESSAGE = 'Member not found'


class MemberAlreadyExists(NotFound):
    CODE = ErrorCode.MEMBER_ALREADY_EXISTS
    MESSAGE = 'A member with this email already exists'
