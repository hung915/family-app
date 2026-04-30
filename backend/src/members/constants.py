from enum import StrEnum


class MemberRole(StrEnum):
    FATHER = 'father'
    MOTHER = 'mother'
    CHILD = 'child'
    SIBLING = 'sibling'
    UNBORN = 'unborn'  # baby in the womb; graduates to CHILD at birth


class ErrorCode(StrEnum):
    MEMBER_NOT_FOUND = 'MEMBER_NOT_FOUND'
    MEMBER_ALREADY_EXISTS = 'MEMBER_ALREADY_EXISTS'
