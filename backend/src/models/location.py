"""
Location tracking model for driver/rider GPS coordinates.
"""

from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, String, Float, DateTime, Index
from .mixins import TimestampMixin, UUIDMixin
from .enums import UserRole


class LocationBase(SQLModel):
    """Base location fields for GPS tracking."""
    user_id: str = Field(foreign_key="users.id", description="Reference to user from users table")
    latitude: float = Field(description="GPS latitude coordinate")
    longitude: float = Field(description="GPS longitude coordinate") 
    role: str = Field(max_length=20, description="User role: driver or rider")


class Location(LocationBase, UUIDMixin, TimestampMixin, table=True):
    """Location tracking table for GPS coordinates."""
    __tablename__ = "locations"
    
    # Add database constraints and indexes for performance
    __table_args__ = (
        # Index for fast lookups by user_id (most common query)
        Index('idx_locations_user_id', 'user_id'),
        # Index for role-based filtering
        Index('idx_locations_role', 'role'),
        # Composite index for user + timestamp (get latest location per user)
        Index('idx_locations_user_updated', 'user_id', 'updated_at'),
    )
    
    # Override columns with specific database types for better performance
    latitude: float = Field(sa_column=Column(Float(precision=10), nullable=False))
    longitude: float = Field(sa_column=Column(Float(precision=10), nullable=False))
    role: str = Field(sa_column=Column(String(20), nullable=False))


class LocationUpdate(SQLModel):
    """Schema for updating location coordinates."""
    latitude: float = Field(ge=-90, le=90, description="Latitude must be between -90 and 90")
    longitude: float = Field(ge=-180, le=180, description="Longitude must be between -180 and 180")
    role: Optional[str] = Field(default=None, description="Optional role update")


class LocationResponse(SQLModel):
    """Response schema for location data."""
    id: str
    user_id: str
    latitude: float
    longitude: float
    role: str
    created_at: str
    updated_at: Optional[str] = None
