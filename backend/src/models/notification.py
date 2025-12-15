"""
Notification model for storing user notifications.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Column, String, DateTime, Text, JSON
from sqlalchemy import Index
from .mixins import TimestampMixin, UUIDMixin


class NotificationBase(SQLModel):
    """Base notification fields."""
    user_id: str = Field(foreign_key="users.id", description="User who receives the notification")
    notification_type: str = Field(max_length=50, description="Type of notification (trip_request, trip_cancelled, etc.)")
    title: str = Field(max_length=200, description="Notification title")
    message: str = Field(description="Notification message content")
    data: Optional[dict] = Field(default=None, sa_column=Column(JSON, nullable=True), description="Additional notification data")
    is_read: bool = Field(default=False, description="Whether the notification has been read")
    read_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True), description="When notification was read")


class Notification(NotificationBase, UUIDMixin, TimestampMixin, table=True):
    """Notification table for storing user notifications."""
    __tablename__ = "notifications"
    
    # Add database constraints and indexes for performance
    __table_args__ = (
        # Index for fast lookups by user_id (most common query)
        Index('idx_notifications_user_id', 'user_id'),
        # Index for unread notifications
        Index('idx_notifications_is_read', 'is_read'),
        # Index for notification type filtering
        Index('idx_notifications_type', 'notification_type'),
        # Composite index for user + unread (common query pattern)
        Index('idx_notifications_user_unread', 'user_id', 'is_read'),
        # Composite index for user + created_at (for sorting)
        Index('idx_notifications_user_created', 'user_id', 'created_at'),
    )
