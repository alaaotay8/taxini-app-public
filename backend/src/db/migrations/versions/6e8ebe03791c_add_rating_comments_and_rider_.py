"""add_rating_comments_and_rider_confirmation

Revision ID: 6e8ebe03791c
Revises: f55c738ed22g
Create Date: 2025-11-27 10:39:04.991515

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e8ebe03791c'
down_revision: Union[str, Sequence[str], None] = 'f55c738ed22g'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add rating comment fields
    op.add_column('trips', sa.Column('rider_rating_comment', sa.String(length=500), nullable=True))
    op.add_column('trips', sa.Column('driver_rating_comment', sa.String(length=500), nullable=True))
    
    # Add rider confirmation of completion fields
    op.add_column('trips', sa.Column('rider_confirmed_completion', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('trips', sa.Column('rider_confirmed_completion_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('trips', 'rider_confirmed_completion_at')
    op.drop_column('trips', 'rider_confirmed_completion')
    op.drop_column('trips', 'driver_rating_comment')
    op.drop_column('trips', 'rider_rating_comment')
