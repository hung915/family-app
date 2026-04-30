"""add_email_to_member

Revision ID: 98bf38ad3655
Revises: f8df03f05926
Create Date: 2026-04-30 08:48:47.957416+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = '98bf38ad3655'
down_revision: str | None = 'f8df03f05926'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('member', sa.Column('email', sa.String(256), nullable=True))
    op.create_unique_constraint('uq_member_email', 'member', ['email'])


def downgrade() -> None:
    op.drop_constraint('uq_member_email', 'member', type_='unique')
    op.drop_column('member', 'email')
