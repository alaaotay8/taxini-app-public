"""
Tests for the admin API endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, select, func

from src.app import app
from src.models.user import User, Driver, Admin
from src.models.trip import Trip
from src.models.settings import Settings
from src.models.enums import UserRole
from src.services.auth import AuthService
from src.services.admin_auth import AdminAuthService
from src.api.v1.admin import require_admin


@pytest.fixture
def client():
    """Create a test client for the app."""
    return TestClient(app)


@pytest.fixture
def admin_user_and_token(session: Session):
    """Create an admin user and return both user and token."""
    # Create an admin user in the test database
    admin_user = User(
        auth_id="admin-auth-id",
        name="Admin User",
        email="admin@taxini.com",
        phone_number="+1234567890",
        role="admin",
        auth_status="verified"
    )
    session.add(admin_user)
    session.commit()
    session.refresh(admin_user)
    
    # Create admin profile
    admin_profile = Admin(
        user_id=admin_user.id,
        test_column="admin123"
    )
    session.add(admin_profile)
    session.commit()
    
    # Generate admin token
    auth_service = AdminAuthService()
    token = auth_service.create_admin_token(admin_user.id, admin_user.email)
    
    return admin_user, token


@pytest.fixture
def admin_headers(admin_user_and_token):
    """Provide admin authentication headers."""
    _, token = admin_user_and_token
    return {
        "Authorization": f"Bearer {token}",
        "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
    }


@pytest.fixture
def mock_admin_user(monkeypatch, test_db_session):
    """Mock an admin user for testing admin endpoints."""
    # Create an admin user in the test database
    admin_user = User(
        auth_id="admin-auth-id",
        name="Admin User",
        email="admin@example.com",
        phone_number="+1234567890",
        role="admin",
        auth_status="verified"
    )
    test_db_session.add(admin_user)
    test_db_session.commit()
    test_db_session.refresh(admin_user)
    
    # Create admin profile
    admin_profile = Admin(
        user_id=admin_user.id,
        test_column="admin123"  # Password field
    )
    test_db_session.add(admin_profile)
    test_db_session.commit()
    
    # Mock the get_current_user_dependency to return admin user
    from src.schemas.auth import CurrentUser
    
    def mock_get_current_user_dependency(*args, **kwargs):
        return CurrentUser(
            auth_id=admin_user.auth_id,
            email=admin_user.email,
            phone=admin_user.phone_number
        )
    
    monkeypatch.setattr(
        AuthService, 
        "get_current_user_dependency", 
        mock_get_current_user_dependency
    )
    
    return admin_user


def test_require_admin_dependency(mock_admin_user, test_db_session):
    """Test the require_admin dependency allows admin users."""
    from src.schemas.auth import CurrentUser
    
    admin_current_user = CurrentUser(
        auth_id=mock_admin_user.auth_id,
        email=mock_admin_user.email,
        phone=mock_admin_user.phone_number
    )
    
    # This should not raise an exception for admin user
    result = require_admin(admin_current_user, test_db_session)
    assert result == admin_current_user


def test_require_admin_dependency_non_admin(test_db_session):
    """Test the require_admin dependency rejects non-admin users."""
    from src.schemas.auth import CurrentUser
    from fastapi import HTTPException
    
    # Create a rider user in the test database
    rider_user = User(
        auth_id="rider-auth-id",
        name="Rider User",
        email="rider@example.com",
        phone_number="+1987654321",
        role="rider",
        auth_status="verified"
    )
    test_db_session.add(rider_user)
    test_db_session.commit()
    test_db_session.refresh(rider_user)
    
    rider_current_user = CurrentUser(
        auth_id=rider_user.auth_id,
        email=rider_user.email,
        phone=rider_user.phone_number
    )
    
    # This should raise an HTTPException for non-admin user
    with pytest.raises(HTTPException) as excinfo:
        require_admin(rider_current_user, test_db_session)
    
    assert excinfo.value.status_code == 403
    assert "Admin privileges required" in str(excinfo.value.detail)


def test_get_admin_dashboard(client, mock_admin_user, test_db_session):
    """Test the admin dashboard endpoint."""
    # Add some test users
    for i in range(3):
        user = User(
            auth_id=f"driver-{i}",
            name=f"Driver {i}",
            email=f"driver{i}@example.com",
            phone_number=f"+100000000{i}",
            role="driver",
            auth_status="verified"
        )
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        
        driver = Driver(
            user_id=user.id,
            taxi_number=f"TAXI-{i}",
            account_status="verified",
            driver_status="offline"
        )
        test_db_session.add(driver)
    
    for i in range(2):
        user = User(
            auth_id=f"rider-{i}",
            name=f"Rider {i}",
            email=f"rider{i}@example.com",
            phone_number=f"+200000000{i}",
            role="rider",
            auth_status="verified"
        )
        test_db_session.add(user)
    
    test_db_session.commit()
    
    # Test dashboard endpoint
    response = client.get("/api/v1/admin/dashboard")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["statistics"]["total_users"] >= 6  # 3 drivers + 2 riders + 1 admin
    assert data["statistics"]["total_drivers"] >= 3
    assert data["statistics"]["total_riders"] >= 2


def test_get_all_drivers(client, mock_admin_user, test_db_session):
    """Test the get all drivers endpoint."""
    response = client.get("/api/v1/admin/drivers")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "pagination" in data


def test_get_all_riders(client, mock_admin_user, test_db_session):
    """Test the get all riders endpoint."""
    response = client.get("/api/v1/admin/riders")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "pagination" in data


def test_update_driver_account_status(client, mock_admin_user, test_db_session):
    """Test updating a driver's account status."""
    # Create a test driver
    driver_user = User(
        auth_id="test-driver",
        name="Test Driver",
        email="testdriver@example.com",
        phone_number="+9876543210",
        role="driver",
        auth_status="verified"
    )
    test_db_session.add(driver_user)
    test_db_session.commit()
    test_db_session.refresh(driver_user)
    
    driver_profile = Driver(
        user_id=driver_user.id,
        taxi_number="TEST-123",
        account_status="locked",
        driver_status="offline"
    )
    test_db_session.add(driver_profile)
    test_db_session.commit()
    
    # Update account status
    response = client.put(
        f"/api/v1/admin/drivers/{driver_user.id}/account-status?account_status=verified"
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    
    # Verify status was updated
    updated_driver = test_db_session.exec(
        select(Driver).where(Driver.user_id == driver_user.id)
    ).first()
    assert updated_driver.account_status == "verified"


# New tests for the enhanced admin features

def test_admin_login_endpoint(client: TestClient, session: Session):
    """Test admin login endpoint."""
    # Create admin user first
    admin_user = User(
        auth_id="login-test-admin",
        name="Login Test Admin",
        email="admin@taxini.com",
        phone_number="+12345678900",
        role="admin",
        auth_status="verified"
    )
    session.add(admin_user)
    session.commit()
    session.refresh(admin_user)
    
    admin_profile = Admin(
        user_id=admin_user.id,
        test_column="admin_data"
    )
    session.add(admin_profile)
    session.commit()
    
    headers = {"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"}
    
    response = client.post(
        "/api/v1/admin/login",
        headers=headers,
        json={"email": "admin@taxini.com", "password": "Admin@123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data
    assert "admin_id" in data


def test_admin_statistics_endpoint_integration(client: TestClient, admin_headers, session: Session):
    """Test integration of admin statistics endpoint."""
    response = client.get("/api/v1/admin/statistics/global", headers=admin_headers)
    
    # Should work even with empty database
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    
    stats = data["data"]
    required_fields = [
        "total_users", "total_drivers", "total_riders", "active_drivers",
        "total_trips", "completed_trips", "cancelled_trips", "completion_rate"
    ]
    for field in required_fields:
        assert field in stats


def test_admin_settings_endpoint_integration(client: TestClient, admin_headers, session: Session):
    """Test integration of admin settings endpoints."""
    # Create a test setting
    setting = Settings(
        setting_key="test_setting",
        setting_value="test_value",
        data_type="string",
        description="Test setting for integration",
        category="test",
        is_active=True,
        is_editable=True
    )
    session.add(setting)
    session.commit()
    
    # Test GET all settings
    response = client.get("/api/v1/admin/settings", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1
    
    # Test GET specific setting
    response = client.get("/api/v1/admin/settings/test_setting", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["setting_key"] == "test_setting"
    
    # Test PUT setting update
    response = client.put(
        "/api/v1/admin/settings/test_setting",
        headers=admin_headers,
        json={"setting_value": "updated_value"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["setting_value"] == "updated_value"


def test_admin_trips_endpoint_integration(client: TestClient, admin_headers, session: Session):
    """Test integration of admin trips endpoints."""
    # Create test user and trip
    rider = User(
        auth_id="test-trip-rider",
        name="Test Trip Rider",
        email="triprider@example.com",
        phone_number="+1111111111",
        role="rider",
        auth_status="verified"
    )
    session.add(rider)
    session.commit()
    session.refresh(rider)
    
    trip = Trip(
        rider_id=rider.id,
        pickup_latitude=36.8065,
        pickup_longitude=10.1815,
        pickup_address="Test Pickup Address",
        destination_latitude=36.8190,
        destination_longitude=10.1658,
        destination_address="Test Destination Address",
        status="completed",
        trip_type="regular",
        estimated_distance_km=10.0,
        estimated_cost_tnd=20.0,
        created_at=session.exec(select(func.now())).scalar()
    )
    session.add(trip)
    session.commit()
    session.refresh(trip)
    
    # Test GET all trips
    response = client.get("/api/v1/admin/trips", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1
    assert "pagination" in data
    
    # Test GET specific trip
    response = client.get(f"/api/v1/admin/trips/{trip.id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == str(trip.id)


def test_admin_endpoints_require_authentication(client: TestClient):
    """Test that all new admin endpoints require authentication."""
    endpoints = [
        "/api/v1/admin/statistics/global",
        "/api/v1/admin/settings",
        "/api/v1/admin/settings/test_key",
        "/api/v1/admin/trips",
        "/api/v1/admin/trips/test-id"
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401
        
        # Test with invalid token
        headers = {
            "Authorization": "Bearer invalid_token",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        response = client.get(endpoint, headers=headers)
        assert response.status_code == 401


def test_admin_endpoints_require_api_key(client: TestClient, admin_user_and_token):
    """Test that all admin endpoints require API key."""
    _, token = admin_user_and_token
    
    endpoints = [
        "/api/v1/admin/statistics/global",
        "/api/v1/admin/settings",
        "/api/v1/admin/trips"
    ]
    
    headers_without_api_key = {"Authorization": f"Bearer {token}"}
    
    for endpoint in endpoints:
        response = client.get(endpoint, headers=headers_without_api_key)
        assert response.status_code == 401


def test_admin_endpoints_error_handling(client: TestClient, admin_headers):
    """Test error handling for admin endpoints."""
    # Test non-existent setting
    response = client.get("/api/v1/admin/settings/nonexistent", headers=admin_headers)
    assert response.status_code == 404
    
    # Test non-existent trip
    fake_trip_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/admin/trips/{fake_trip_id}", headers=admin_headers)
    assert response.status_code == 404
    
    # Test invalid date format in statistics
    response = client.get(
        "/api/v1/admin/statistics/global?start_date=invalid-date",
        headers=admin_headers
    )
    assert response.status_code == 422


def test_admin_pagination_validation(client: TestClient, admin_headers):
    """Test pagination parameter validation."""
    # Test invalid page number
    response = client.get("/api/v1/admin/trips?page=-1", headers=admin_headers)
    assert response.status_code == 422
    
    # Test invalid page size
    response = client.get("/api/v1/admin/trips?page_size=1000", headers=admin_headers)
    assert response.status_code == 422
    
    # Test valid pagination
    response = client.get("/api/v1/admin/trips?page=1&page_size=10", headers=admin_headers)
    assert response.status_code == 200
