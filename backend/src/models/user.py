"""
User-related SQLModel definitions.

This module contains the base User model and role-specific extensions.
"""

from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, String
from .enums import UserRole, DriverAccountStatus, DriverStatus
from .mixins import TimestampMixin, UUIDMixin


class UserBase(SQLModel):
    """Base user fields shared across create/update/read operations."""
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(max_length=255, regex=r'^[^@]+@[^@]+\.[^@]+$', unique=True)
    phone_number: str = Field(max_length=20, regex=r'^\+?1?\d{9,15}$', unique=True)
    role: UserRole
    auth_id: str = Field(index=True)  # Reference to Supabase auth user ID


class User(UserBase, UUIDMixin, TimestampMixin, table=True):
    """Main user table - parent table for all user types."""
    __tablename__ = "users"
    
    role: str = Field(sa_column=Column(String(20), name="role"))
    auth_status: str = Field(default="pending", sa_column=Column(String(20), name="auth_status"))
    
    # Override with unique constraints
    email: str = Field(max_length=255, regex=r'^[^@]+@[^@]+\.[^@]+$', unique=True, index=True)
    phone_number: str = Field(max_length=20, regex=r'^\+?1?\d{9,15}$', unique=True, index=True)
    
    # Relationships to role-specific tables
    rider_profile: Optional["Rider"] = Relationship(back_populates="user")
    driver_profile: Optional["Driver"] = Relationship(back_populates="user")
    admin_profile: Optional["Admin"] = Relationship(back_populates="user")
    
    # Relationship to tickets
    tickets: List["Ticket"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Ticket.user_id"},
        back_populates="user"
    )
    
    # Relationship to trips
    rider_trips: List["Trip"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Trip.rider_id"},
        back_populates="rider"
    )
    driver_trips: List["Trip"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Trip.driver_id"},
        back_populates="driver"
    )


class RiderBase(SQLModel):
    """Base rider fields."""
    residence_place: str = Field(max_length=255)


class Rider(RiderBase, UUIDMixin, TimestampMixin, table=True):
    """Rider-specific table."""
    __tablename__ = "riders"
    
    user_id: str = Field(foreign_key="users.id", unique=True)
    user: User = Relationship(back_populates="rider_profile")


class DriverBase(SQLModel):
    """Base driver fields."""
    # Keep database columns as plain strings; URL validation is enforced in request/response schemas
    id_card: Optional[str] = Field(default=None, max_length=500)  # Image URL/path
    driver_license: Optional[str] = Field(default=None, max_length=500)  # Image URL/path
    taxi_number: str = Field(max_length=50)
    account_status: str = Field(default="locked", max_length=20)  # locked, verified, banned
    driver_status: str = Field(default="offline", max_length=20)  # offline, online, on_trip


class Driver(DriverBase, UUIDMixin, TimestampMixin, table=True):
    """Driver-specific table."""
    __tablename__ = "drivers"
    
    user_id: str = Field(foreign_key="users.id", unique=True)
    user: User = Relationship(back_populates="driver_profile")


class AdminBase(SQLModel):
    """Base admin fields."""
    test_column: Optional[str] = Field(default=None, max_length=255)


class Admin(AdminBase, UUIDMixin, TimestampMixin, table=True):
    """Admin-specific table."""
    __tablename__ = "admins"
    
    user_id: str = Field(foreign_key="users.id", unique=True)
    user: User = Relationship(back_populates="admin_profile")
