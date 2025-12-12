"""merge_heads

Revision ID: aed2403cbf49
Revises: 7db8928812ce, b2be6f78276a
Create Date: 2025-11-13 21:01:56.610362

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aed2403cbf49'
down_revision: Union[str, Sequence[str], None] = ('7db8928812ce', 'b2be6f78276a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
