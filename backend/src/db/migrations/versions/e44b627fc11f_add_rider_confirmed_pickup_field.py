"""add_rider_confirmed_pickup_field

Revision ID: e44b627fc11f
Revises: d4f5e6a7b8c9
Create Date: 2025-11-25 11:18:07.205185

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e44b627fc11f'
down_revision: Union[str, Sequence[str], None] = 'd4f5e6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add rider_confirmed_pickup and rider_confirmed_at columns to trips table
    op.add_column('trips', sa.Column('rider_confirmed_pickup', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('trips', sa.Column('rider_confirmed_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove rider confirmation columns
    op.drop_column('trips', 'rider_confirmed_at')
    op.drop_column('trips', 'rider_confirmed_pickup')
