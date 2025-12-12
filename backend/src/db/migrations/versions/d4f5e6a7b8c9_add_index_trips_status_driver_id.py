"""add_index_trips_status_driver_id

Revision ID: d4f5e6a7b8c9
Revises: aed2403cbf49
Create Date: 2025-11-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4f5e6a7b8c9'
down_revision: Union[str, Sequence[str], None] = 'aed2403cbf49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add composite index on trips (status, driver_id) for faster pending requests queries."""
    op.create_index(
        'idx_trips_status_driver_id',
        'trips',
        ['status', 'driver_id'],
        unique=False
    )


def downgrade() -> None:
    """Remove the composite index."""
    op.drop_index('idx_trips_status_driver_id', table_name='trips')
