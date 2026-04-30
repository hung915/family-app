import enum
import uuid

from sqlalchemy import Column, Date, Enum, String
from sqlalchemy.dialects.postgresql import UUID

from src.database import Base


class MemberRole(str, enum.Enum):  # noqa: UP042
    FATHER = 'father'
    MOTHER = 'mother'
    CHILD = 'child'
    SIBLING = 'sibling'
    UNBORN = 'unborn'  # for the baby in the womb


class Member(Base):
    __tablename__ = 'member'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(128), nullable=False)
    nickname = Column(String(128))
    role = Column(Enum(MemberRole), nullable=False)
    birth_date = Column(Date)  # null for unborn
    due_date = Column(Date)  # only for unborn
