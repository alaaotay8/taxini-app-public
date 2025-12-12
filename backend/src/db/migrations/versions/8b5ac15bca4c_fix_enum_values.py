"""Fix enum values

Revision ID: 8b5ac15bca4c
Revises: b01e82142b4a
Create Date: 2025-08-11 13:15:20.213448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b5ac15bca4c'
down_revision: Union[str, Sequence[str], None] = 'b01e82142b4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Fix the enum values by altering the columns to use string temporarily
    # then recreating the enums
    
    # First, alter the columns to use VARCHAR temporarily
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(20)")
    op.execute("ALTER TABLE users ALTER COLUMN auth_status TYPE VARCHAR(20)")
    
    # Drop the old enum types
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS authstatus")
    
    # Recreate the enum types with correct values
    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'driver', 'rider')")
    op.execute("CREATE TYPE authstatus AS ENUM ('pending', 'verified', 'suspended')")
    
    # Convert the columns back to use the enum types
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole")
    op.execute("ALTER TABLE users ALTER COLUMN auth_status TYPE authstatus USING auth_status::authstatus")


def downgrade() -> None:
    """Downgrade schema."""
    # Revert back to the original enum setup
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(20)")
    op.execute("ALTER TABLE users ALTER COLUMN auth_status TYPE VARCHAR(20)")
    
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS authstatus")
    
    # Recreate with the problematic setup (for rollback purposes)
    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'driver', 'rider')")
    op.execute("CREATE TYPE authstatus AS ENUM ('pending', 'verified', 'suspended')")
    
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole")
    op.execute("ALTER TABLE users ALTER COLUMN auth_status TYPE authstatus USING auth_status::authstatus")
