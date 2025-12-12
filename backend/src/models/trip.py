"""
Trip model for managing ride requests and assignments.

This module contains the Trip model that represents a ride request from a rider
and its assignment to a driver.
"""

from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, String, Float, DateTime, Text
from datetime import datetime
from .mixins import TimestampMixin, UUIDMixin


class TripBase(SQLModel):
    """Base trip fields shared across create/update/read operations."""
    rider_id: str = Field(foreign_key="users.id")
    driver_id: Optional[str] = Field(default=None, foreign_key="users.id")
    
    # Pickup location
    pickup_latitude: float = Field(ge=-90, le=90)
    pickup_longitude: float = Field(ge=-180, le=180)
    pickup_address: Optional[str] = Field(default=None, max_length=500)
    
    # Destination location
    destination_latitude: float = Field(ge=-90, le=90)
    destination_longitude: float = Field(ge=-180, le=180)
    destination_address: Optional[str] = Field(default=None, max_length=500)
    
    # Trip details
    trip_type: str = Field(default="regular", max_length=50)  # regular, express, scheduled
    estimated_distance_km: Optional[float] = Field(default=None, ge=0)
    estimated_cost_tnd: Optional[float] = Field(default=None, ge=0)  # Cost in Tunisian Dinars
    
    # Cost breakdown (Approach fee + Meter cost)
    approach_distance_km: Optional[float] = Field(default=None, ge=0)  # Distance from driver to pickup
    approach_fee_tnd: Optional[float] = Field(default=None, ge=0)  # Frais d'approche (FA)
    meter_cost_tnd: Optional[float] = Field(default=None, ge=0)  # Final meter reading from driver
    total_cost_tnd: Optional[float] = Field(default=None, ge=0)  # FA + meter_cost
    
    # Status and timestamps
    status: str = Field(default="requested", max_length=20)
    requested_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    assigned_at: Optional[datetime] = Field(default=None)
    accepted_at: Optional[datetime] = Field(default=None)
    rider_confirmed_pickup: Optional[bool] = Field(default=False)  # Rider confirms driver arrived
    rider_confirmed_at: Optional[datetime] = Field(default=None)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    cancelled_at: Optional[datetime] = Field(default=None)
    
    # Notes
    rider_notes: Optional[str] = Field(default=None, max_length=1000)
    driver_notes: Optional[str] = Field(default=None, max_length=1000)
    cancellation_reason: Optional[str] = Field(default=None, max_length=500)
    
    # Rating (post-trip)
    rider_rating: Optional[int] = Field(default=None, ge=1, le=5)
    rider_rating_comment: Optional[str] = Field(default=None, max_length=500)
    driver_rating: Optional[int] = Field(default=None, ge=1, le=5)
    driver_rating_comment: Optional[str] = Field(default=None, max_length=500)
    
    # Rider confirmation of completion
    rider_confirmed_completion: Optional[bool] = Field(default=False)
    rider_confirmed_completion_at: Optional[datetime] = Field(default=None)


class Trip(TripBase, UUIDMixin, TimestampMixin, table=True):
    """Trip table - represents a ride request and its lifecycle."""
    __tablename__ = "trips"
    
    # Use string columns for status to avoid enum issues
    status: str = Field(sa_column=Column(String(20), name="status"))
    trip_type: str = Field(sa_column=Column(String(50), name="trip_type"))
    
    # Relationships
    rider: Optional["User"] = Relationship(
        back_populates="rider_trips",
        sa_relationship_kwargs={"foreign_keys": "[Trip.rider_id]"}
    )
    driver: Optional["User"] = Relationship(
        back_populates="driver_trips", 
        sa_relationship_kwargs={"foreign_keys": "[Trip.driver_id]"}
    )


# Import Enum at the top where it belongs
from enum import Enum
