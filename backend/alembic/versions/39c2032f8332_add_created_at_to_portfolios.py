"""add created_at to portfolios

Revision ID: 39c2032f8332
Revises: 0cfc8b7becd5
Create Date: 2025-12-19 12:48:42.890250

"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39c2032f8332'
down_revision: Union[str, None] = '0cfc8b7becd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch operations for SQLite compatibility
    with op.batch_alter_table('portfolios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text("(datetime('now'))")))


def downgrade() -> None:
    with op.batch_alter_table('portfolios', schema=None) as batch_op:
        batch_op.drop_column('created_at')
