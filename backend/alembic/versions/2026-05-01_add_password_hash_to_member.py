"""add_password_hash_to_member

Revision ID: a3c7e1f28b90
Revises: 98bf38ad3655
Create Date: 2026-05-01 00:00:00.000000+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = 'a3c7e1f28b90'
down_revision: str | None = '98bf38ad3655'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('member', sa.Column('password_hash', sa.String(256), nullable=True))


def downgrade() -> None:
    op.drop_column('member', 'password_hash')
