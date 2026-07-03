"""add_interview_report_url

Revision ID: 3f1b9c4a2d7e
Revises: 847fabda1674
Create Date: 2026-07-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f1b9c4a2d7e'
down_revision: Union[str, Sequence[str], None] = '847fabda1674'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('interviews', sa.Column('report_url', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('interviews', 'report_url')
