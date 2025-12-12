"""
Test the location tracking service.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from sqlmodel import Session, select
from src.models.location import Location
from src.models.user import User, Driver
from src.services.location import LocationService


def test_upsert_location_new_user(session: Session):
    """Test creating a new location entry for a user."""
    # Create a test user
    user = User(id="test-user-id-123", name="Test User", role="driver", 
                email="test123@example.com", phone_number="+12345678901", auth_id="auth_id_test_123")
    session.add(user)
    session.commit()
    
    # Upsert location for this user
    result = LocationService.upsert_location(
        session=session,
        user_id=user.id,
        latitude=33.8938,
        longitude=35.5018,
        role="driver"
    )
    
    # Verify result
    assert result["success"] is True
    assert "Location updated successfully" in result["message"]
    assert result["location"].user_id == user.id
    assert result["location"].latitude == 33.8938
    assert result["location"].longitude == 35.5018
    assert result["location"].role == "driver"
    
    # Check that the location was actually saved in the database
    saved_location = session.exec(select(Location).where(Location.user_id == user.id)).first()
    assert saved_location is not None
    assert saved_location.latitude == 33.8938
    assert saved_location.longitude == 35.5018


def test_upsert_location_nonexistent_user(session: Session):
    """Test updating location for a user that doesn't exist."""
    result = LocationService.upsert_location(
        session=session,
        user_id="nonexistent-user",
        latitude=33.8938,
        longitude=35.5018,
        role="driver"
    )
    
    # Verify result
    assert result["success"] is False
    assert "not found" in result["message"]
    assert result["error"] == "USER_NOT_FOUND"


def test_upsert_location_update_existing(session: Session):
    """Test updating an existing location entry for a user."""
    # Create a test user
    user = User(id="test-user-id-456", name="Test User", role="driver", 
                email="test456@example.com", phone_number="+12345678902", auth_id="auth_id_test_456")
    session.add(user)
    session.commit()
    
    # Create initial location
    location = Location(
        user_id=user.id,
        latitude=33.8938,
        longitude=35.5018,
        role="driver"
    )
    session.add(location)
    session.commit()
    
    # Update location
    result = LocationService.upsert_location(
        session=session,
        user_id=user.id,
        latitude=33.9108,
        longitude=35.5178,
        role="driver"
    )
    
    # Verify result
    assert result["success"] is True
    assert "Location updated successfully" in result["message"]
    assert result["location"].user_id == user.id
    assert result["location"].latitude == 33.9108
    assert result["location"].longitude == 35.5178
    
    # Check database
    saved_location = session.exec(select(Location).where(Location.user_id == user.id)).first()
    assert saved_location is not None
    assert saved_location.latitude == 33.9108
    assert saved_location.longitude == 35.5178


def test_get_user_location(session: Session):
    """Test getting a user's location."""
    # Create a test user
    user = User(id="test-user-id-789", name="Test User", role="driver", 
                email="test789@example.com", phone_number="+12345678903", auth_id="auth_id_test_789")
    session.add(user)
    session.commit()
    
    # Create location
    location = Location(
        user_id=user.id,
        latitude=33.8938,
        longitude=35.5018,
        role="driver"
    )
    session.add(location)
    session.commit()
    
    # Get location
    result = LocationService.get_user_location(session, user.id)
    
    # Verify result
    assert result is not None
    assert result.user_id == user.id
    assert result.latitude == 33.8938
    assert result.longitude == 35.5018
    assert result.role == "driver"


def test_get_user_location_nonexistent(session: Session):
    """Test getting location for a user that doesn't exist."""
    result = LocationService.get_user_location(session, "nonexistent-user")
    assert result is None


