"""
Ticket model for user support requests and issue tracking.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, String, DateTime, Text, Index
from .mixins import TimestampMixin, UUIDMixin
from .enums import UserRole
from enum import Enum


class TicketStatus(str, Enum):
    """Ticket status enumeration."""
    OPEN = "open"           # Default - newly created ticket
    IN_PROGRESS = "in_progress"  # Being processed by admin
    RESOLVED = "resolved"    # Issue has been resolved
    CLOSED = "closed"        # Ticket closed (with or without resolution)
    
    def __str__(self):
        return self.value


class TicketPriority(str, Enum):
    """Ticket priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    
    def __str__(self):
        return self.value


class TicketBase(SQLModel):
    """Base ticket fields shared across create/update/read operations."""
    title: str = Field(min_length=5, max_length=100, description="Brief description of the issue")
    content: str = Field(min_length=10, description="Detailed description of the issue")
    user_id: str = Field(foreign_key="users.id", description="Reference to the user who created the ticket")
    user_role: UserRole = Field(description="Role of the user who created the ticket")
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM, description="Ticket priority level")
    issue_at: Optional[datetime] = Field(default=None, description="When the issue occurred")


class Ticket(TicketBase, UUIDMixin, TimestampMixin, table=True):
    """Main ticket table for storing user issues and support requests."""
    __tablename__ = "tickets"
    
    # Add database constraints and indexes for performance
    __table_args__ = (
        # Index for fast lookups by user_id (common query for user's tickets)
        Index('idx_tickets_user_id', 'user_id'),
        # Index for status filtering (common admin operation)
        Index('idx_tickets_status', 'status'),
        # Index for priority sorting
        Index('idx_tickets_priority', 'priority'),
        # Composite index for status + created_at (common sorting pattern)
        Index('idx_tickets_status_created', 'status', 'created_at'),
    )
    
    # Override columns with specific database types
    content: str = Field(sa_column=Column(Text, nullable=False))
    status: TicketStatus = Field(
        default=TicketStatus.OPEN, 
        sa_column=Column(String(20), nullable=False),
        description="Current status of the ticket"
    )
    admin_notes: Optional[str] = Field(
        default=None, 
        sa_column=Column(Text, nullable=True),
        description="Private notes added by admin"
    )
    resolved_at: Optional[datetime] = Field(
        default=None, 
        sa_column=Column(DateTime, nullable=True),
        description="When the ticket was resolved"
    )
    resolved_by: Optional[str] = Field(
        default=None, 
        foreign_key="users.id", 
        description="Reference to the admin who resolved the ticket"
    )
    
    # Relationship to user (optional for better typing support)
    user: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Ticket.user_id"},
        back_populates="tickets"
    )
    resolver: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Ticket.resolved_by"}
    )


class TicketUpdate(SQLModel):
    """Schema for updating ticket information."""
    title: Optional[str] = Field(default=None, min_length=5, max_length=100)
    content: Optional[str] = Field(default=None, min_length=10)
    status: Optional[TicketStatus] = Field(default=None)
    priority: Optional[TicketPriority] = Field(default=None)
    admin_notes: Optional[str] = Field(default=None)
