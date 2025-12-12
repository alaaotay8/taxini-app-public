"""convert_enum_columns_to_varchar

Revision ID: 923ccf97cd1d
Revises: 8b5ac15bca4c
Create Date: 2025-08-11 13:33:26.794085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '923ccf97cd1d'
down_revision: Union[str, Sequence[str], None] = '8b5ac15bca4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Convert enum columns to varchar
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(20)")
    op.execute("ALTER TABLE users ALTER COLUMN auth_status TYPE VARCHAR(20)")


def downgrade() -> None:
    """Downgrade schema."""
    # Convert back to enum columns
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole")
    op.execute("ALTER TABLE users ALTER COLUMN auth_status TYPE authstatus USING auth_status::authstatus")
