from src.exceptions import NotFound
from src.members.constants import ErrorCode


class MemberNotFound(NotFound):
    def __init__(self) -> None:
        super().__init__(detail=ErrorCode.MEMBER_NOT_FOUND)
