"""create_tickets_table

Revision ID: b2be6f78276a
Revises: None
Create Date: 2025-09-15 10:53:25.745772

This is an independent migration that can be run separately from the main migration chain.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2be6f78276a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if the enum types already exist
    conn = op.get_bind()
    
    # Check if ticket_status enum exists
    check_status_enum = conn.execute(
        """
        SELECT EXISTS (
            SELECT 1 FROM pg_type 
            WHERE typname = 'ticket_status'
        )
        """
    ).scalar()
    
    if not check_status_enum:
        op.execute("CREATE TYPE ticket_status AS ENUM ('open', 'in_progress', 'resolved', 'closed')")
    
    # Check if ticket_priority enum exists
    check_priority_enum = conn.execute(
        """
        SELECT EXISTS (
            SELECT 1 FROM pg_type 
            WHERE typname = 'ticket_priority'
        )
        """
    ).scalar()
    
    if not check_priority_enum:
        op.execute("CREATE TYPE ticket_priority AS ENUM ('low', 'medium', 'high', 'urgent')")
    
    # Check if tickets table already exists
    check_table = conn.execute(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'tickets'
        )
        """
    ).scalar()
    
    if not check_table:
        # Create tickets table
        op.create_table(
            'tickets',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('title', sa.String(100), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('user_role', sa.String(), nullable=False),
            sa.Column('priority', sa.String(), nullable=False, server_default='medium'),
            sa.Column('issue_at', sa.DateTime(), nullable=True),
            sa.Column('status', sa.String(), nullable=False, server_default='open'),
            sa.Column('admin_notes', sa.Text(), nullable=True),
            sa.Column('resolved_at', sa.DateTime(), nullable=True),
            sa.Column('resolved_by', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create indexes if the table exists
    conn = op.get_bind()
    check_table = conn.execute(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'tickets'
        )
        """
    ).scalar()
    
    if check_table:
        # Check if indexes exist
        for idx_name in ['idx_tickets_user_id', 'idx_tickets_status', 'idx_tickets_priority', 'idx_tickets_status_created']:
            check_index = conn.execute(
                f"""
                SELECT EXISTS (
                    SELECT FROM pg_indexes
                    WHERE indexname = '{idx_name}'
                )
                """
            ).scalar()
            
            if not check_index:
                if idx_name == 'idx_tickets_user_id':
                    op.create_index('idx_tickets_user_id', 'tickets', ['user_id'])
                elif idx_name == 'idx_tickets_status':
                    op.create_index('idx_tickets_status', 'tickets', ['status'])
                elif idx_name == 'idx_tickets_priority':
                    op.create_index('idx_tickets_priority', 'tickets', ['priority'])
                elif idx_name == 'idx_tickets_status_created':
                    op.create_index('idx_tickets_status_created', 'tickets', ['status', 'created_at'])


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    
    # Check if the table exists before trying to drop it
    check_table = conn.execute(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'tickets'
        )
        """
    ).scalar()
    
    if check_table:
        # Drop indexes if they exist
        for idx_name in ['idx_tickets_status_created', 'idx_tickets_priority', 'idx_tickets_status', 'idx_tickets_user_id']:
            check_index = conn.execute(
                f"""
                SELECT EXISTS (
                    SELECT FROM pg_indexes
                    WHERE indexname = '{idx_name}'
                )
                """
            ).scalar()
            
            if check_index:
                op.drop_index(idx_name)
        
        # Drop table
        op.drop_table('tickets')
    
    # Check if enums exist before dropping
    check_status_enum = conn.execute(
        """
        SELECT EXISTS (
            SELECT 1 FROM pg_type 
            WHERE typname = 'ticket_status'
        )
        """
    ).scalar()
    
    if check_status_enum:
        op.execute("DROP TYPE ticket_status")
    
    check_priority_enum = conn.execute(
        """
        SELECT EXISTS (
            SELECT 1 FROM pg_type 
            WHERE typname = 'ticket_priority'
        )
        """
    ).scalar()
    
    if check_priority_enum:
        op.execute("DROP TYPE ticket_priority")
