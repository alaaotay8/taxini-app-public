"""Fix enum values for user roles and auth status

Revision ID: b01e82142b4a
Revises: 9d162d8bc493
Create Date: 2025-08-11 13:15:09.465827

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b01e82142b4a'
down_revision: Union[str, Sequence[str], None] = '9d162d8bc493'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
