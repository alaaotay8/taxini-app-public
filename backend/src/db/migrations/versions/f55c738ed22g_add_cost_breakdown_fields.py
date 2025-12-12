"""add_cost_breakdown_fields

Revision ID: f55c738ed22g
Revises: e44b627fc11f
Create Date: 2025-11-25 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f55c738ed22g'
down_revision: Union[str, Sequence[str], None] = 'e44b627fc11f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add cost breakdown fields."""
    # Add approach distance and fee columns
    op.add_column('trips', sa.Column('approach_distance_km', sa.Float(), nullable=True))
    op.add_column('trips', sa.Column('approach_fee_tnd', sa.Float(), nullable=True))
    op.add_column('trips', sa.Column('meter_cost_tnd', sa.Float(), nullable=True))
    op.add_column('trips', sa.Column('total_cost_tnd', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema - remove cost breakdown fields."""
    op.drop_column('trips', 'total_cost_tnd')
    op.drop_column('trips', 'meter_cost_tnd')
    op.drop_column('trips', 'approach_fee_tnd')
    op.drop_column('trips', 'approach_distance_km')
