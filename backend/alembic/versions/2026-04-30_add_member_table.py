"""add_member_table

Revision ID: f8df03f05926
Revises:
Create Date: 2026-04-30 03:52:42.016263+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = 'f8df03f05926'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_MEMBER_ROLE = sa.Enum(
    'father',
    'mother',
    'child',
    'sibling',
    'unborn',
    name='member_role',
)


def upgrade() -> None:
    _MEMBER_ROLE.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'member',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(128), nullable=False),
        sa.Column('nickname', sa.String(64), nullable=True),
        sa.Column('role', _MEMBER_ROLE, nullable=False),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('avatar_url', sa.String(512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_member'),
    )


def downgrade() -> None:
    op.drop_table('member')
    _MEMBER_ROLE.drop(op.get_bind(), checkfirst=True)
