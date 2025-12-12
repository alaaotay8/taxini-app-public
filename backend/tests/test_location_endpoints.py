"""
Test the location tracking API endpoints.
"""

import pytest
import json
from datetime import datetime
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from src.models.location import Location
from src.models.user import User, Driver


def test_update_location_endpoint(client: TestClient, session: Session):
    """Test the update_location endpoint."""
    # Create a test user
    user = User(id="test-api-user-1", name="API Test User", role="driver", 
                email="api_user1@example.com", phone_number="+12345670001", auth_id="auth_id_test_1")
    session.add(user)
    session.commit()
    
    # Call the API
    response = client.post(
        f"/api/v1/locations/update/{user.id}",
        json={"latitude": 33.8938, "longitude": 35.5018, "role": "driver"},
        headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Location updated successfully" in data["message"]
    assert data["location"]["user_id"] == user.id
    assert data["location"]["latitude"] == 33.8938
    assert data["location"]["longitude"] == 35.5018
    assert data["location"]["role"] == "driver"
    
    # Verify database update
    saved_location = session.exec(select(Location).where(Location.user_id == user.id)).first()
    assert saved_location is not None
    assert saved_location.latitude == 33.8938
    assert saved_location.longitude == 35.5018


def test_update_location_nonexistent_user(client: TestClient):
    """Test update_location with non-existent user."""
    response = client.post(
        "/api/v1/locations/update/nonexistent-user-id",
        json={"latitude": 33.8938, "longitude": 35.5018, "role": "driver"},
        headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"}
    )
    
    # Check response
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "User with ID nonexistent-user-id not found"


def test_get_user_location_endpoint(client: TestClient, session: Session):
    """Test the get_user_location endpoint."""
    # Create a test user
    user = User(id="test-api-user-2", name="API Test User 2", role="driver", 
                email="api_user2@example.com", phone_number="+12345670002", auth_id="auth_id_test_2")
    session.add(user)
    session.commit()
    
    # Create location
    location = Location(
        user_id=user.id,
        latitude=33.9108,
        longitude=35.5178,
        role="driver"
    )
    session.add(location)
    session.commit()
    
    # Call the API
    response = client.get(f"/api/v1/locations/user/{user.id}",
                         headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"})
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user.id
    assert data["latitude"] == 33.9108
    assert data["longitude"] == 35.5178
    assert data["role"] == "driver"


def test_get_user_location_nonexistent(client: TestClient):
    """Test get_user_location with non-existent user."""
    response = client.get("/api/v1/locations/user/nonexistent-user-id",
                          headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"})
    
    # Check response
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Location not found for user"




def test_delete_user_location_endpoint(client: TestClient, session: Session):
    """Test the delete_user_location endpoint."""
    # Create a test user
    user = User(id="test-api-user-3", name="API Test User 3", role="driver", 
                email="api_user3@example.com", phone_number="+12345670009", auth_id="auth_id_test_3")
    session.add(user)
    session.commit()
    
    # Create location
    location = Location(
        user_id=user.id,
        latitude=33.9108,
        longitude=35.5178,
        role="driver"
    )
    session.add(location)
    session.commit()
    
    # Call the API
    response = client.delete(f"/api/v1/locations/user/{user.id}",
                            headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"})
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Location deleted successfully" in data["message"]
    
    # Verify database deletion
    deleted_location = session.exec(select(Location).where(Location.user_id == user.id)).first()
    assert deleted_location is None
