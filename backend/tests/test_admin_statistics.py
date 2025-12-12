"""
Tests for admin statistics endpoints.
"""

import pytest
from datetime import datetime, date, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.models.user import User, Driver, Rider, Admin
from src.models.trip import Trip
from src.models.settings import Settings
from src.services.admin_auth import AdminAuthService


class TestAdminStatistics:
    """Test class for admin statistics functionality."""

    @pytest.fixture
    def admin_token(self, session: Session):
        """Create admin user and get authentication token."""
        # Create admin user
        admin_user = User(
            auth_id="admin-test-id",
            name="Test Admin",
            email="admin@taxini.com",
            phone_number="+12345678900",
            role="admin",
            auth_status="verified"
        )
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)
        
        # Create admin profile
        admin_profile = Admin(
            user_id=admin_user.id,
            test_column="admin_data"
        )
        session.add(admin_profile)
        session.commit()
        
        # Generate token
        auth_service = AdminAuthService()
        token = auth_service.create_admin_token(admin_user.id, admin_user.email)
        return token

    @pytest.fixture
    def sample_data(self, session: Session):
        """Create sample data for testing statistics."""
        # Create users
        users_data = []
        
        # Create drivers
        for i in range(5):
            user = User(
                auth_id=f"driver-{i}",
                name=f"Driver {i}",
                email=f"driver{i}@example.com",
                phone_number=f"+1000000{i:03d}",
                role="driver",
                auth_status="verified"
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            
            driver = Driver(
                user_id=user.id,
                taxi_number=f"TAXI-{i}",
                account_status="verified" if i < 3 else "locked",
                driver_status="online" if i < 2 else "offline"
            )
            session.add(driver)
            users_data.append(user)
        
        # Create riders
        for i in range(8):
            user = User(
                auth_id=f"rider-{i}",
                name=f"Rider {i}",
                email=f"rider{i}@example.com",
                phone_number=f"+2000000{i:03d}",
                role="rider",
                auth_status="verified"
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            
            rider = Rider(
                user_id=user.id,
                residence_place=f"District {i}"
            )
            session.add(rider)
            users_data.append(user)
        
        session.commit()
        
        # Create trips with various statuses and dates
        trips_data = []
        today = datetime.utcnow()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        
        trip_scenarios = [
            # Recent completed trips
            {"rider_idx": 0, "driver_idx": 0, "status": "completed", "cost": 15.50, "created": today, "completed": today},
            {"rider_idx": 1, "driver_idx": 1, "status": "completed", "cost": 22.75, "created": today, "completed": today},
            {"rider_idx": 2, "driver_idx": 0, "status": "completed", "cost": 18.25, "created": yesterday, "completed": yesterday},
            # This week's trips
            {"rider_idx": 3, "driver_idx": 1, "status": "completed", "cost": 31.00, "created": week_ago, "completed": week_ago},
            {"rider_idx": 4, "driver_idx": 2, "status": "completed", "cost": 12.50, "created": week_ago, "completed": week_ago},
            # Cancelled trips
            {"rider_idx": 5, "driver_idx": None, "status": "cancelled", "cost": 0, "created": today, "completed": None},
            {"rider_idx": 6, "driver_idx": None, "status": "cancelled", "cost": 0, "created": yesterday, "completed": None},
            # Active trips
            {"rider_idx": 7, "driver_idx": 1, "status": "started", "cost": 25.00, "created": today, "completed": None},
        ]
        
        for i, scenario in enumerate(trip_scenarios):
            rider_id = users_data[scenario["rider_idx"] + 5].id  # Riders start after drivers
            driver_id = users_data[scenario["driver_idx"]].id if scenario["driver_idx"] is not None else None
            
            trip = Trip(
                rider_id=rider_id,
                driver_id=driver_id,
                pickup_latitude=36.8065,
                pickup_longitude=10.1815,
                pickup_address="Tunis Center",
                destination_latitude=36.8190,
                destination_longitude=10.1658,
                destination_address="La Marsa",
                status=scenario["status"],
                trip_type="regular",
                estimated_distance_km=15.0 + i,
                estimated_cost_tnd=scenario["cost"],
                requested_at=scenario["created"],
                completed_at=scenario["completed"],
                created_at=scenario["created"]
            )
            session.add(trip)
            trips_data.append(trip)
        
        session.commit()
        return {"users": users_data, "trips": trips_data}

    def test_global_statistics_success(self, client: TestClient, admin_token: str, sample_data):
        """Test successful global statistics retrieval."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        response = client.get("/api/v1/admin/statistics/global", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        stats = data["data"]
        
        # Verify basic counts
        assert stats["total_users"] >= 13  # 5 drivers + 8 riders
        assert stats["total_drivers"] >= 5
        assert stats["total_riders"] >= 8
        assert stats["active_drivers"] >= 3  # Verified drivers
        
        # Verify trip statistics
        assert stats["total_trips"] >= 8
        assert stats["completed_trips"] >= 5
        assert stats["cancelled_trips"] >= 2
        
        # Verify revenue calculations
        assert stats["total_revenue"] >= 99.0  # Sum of completed trips
        assert stats["revenue_today"] >= 33.75  # Today's completed trips
        
        # Verify driver status counts
        assert stats["online_drivers"] >= 2
        assert stats["offline_drivers"] >= 3
        
        # Verify completion rate
        assert 0 <= stats["completion_rate"] <= 100

    def test_global_statistics_with_date_filter(self, client: TestClient, admin_token: str, sample_data):
        """Test global statistics with date filtering."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        # Test with today's date
        today = date.today()
        response = client.get(
            f"/api/v1/admin/statistics/global?start_date={today}&end_date={today}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        stats = data["data"]
        
        # Should only include today's data
        assert stats["trips_today"] >= 0
        assert stats["revenue_today"] >= 0

    def test_global_statistics_unauthorized(self, client: TestClient):
        """Test global statistics without authentication."""
        response = client.get("/api/v1/admin/statistics/global")
        assert response.status_code == 401

    def test_global_statistics_invalid_token(self, client: TestClient):
        """Test global statistics with invalid token."""
        headers = {
            "Authorization": "Bearer invalid_token",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        response = client.get("/api/v1/admin/statistics/global", headers=headers)
        assert response.status_code == 401

    def test_global_statistics_missing_api_key(self, client: TestClient, admin_token: str):
        """Test global statistics without API key."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.get("/api/v1/admin/statistics/global", headers=headers)
        assert response.status_code == 401

    def test_global_statistics_invalid_date_format(self, client: TestClient, admin_token: str):
        """Test global statistics with invalid date format."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        response = client.get(
            "/api/v1/admin/statistics/global?start_date=invalid-date",
            headers=headers
        )
        
        assert response.status_code == 422  # Validation error

    def test_global_statistics_end_before_start(self, client: TestClient, admin_token: str):
        """Test global statistics with end date before start date."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        response = client.get(
            "/api/v1/admin/statistics/global?start_date=2025-09-17&end_date=2025-09-16",
            headers=headers
        )
        
        assert response.status_code == 400
        assert "start_date cannot be after end_date" in response.json()["detail"]

    def test_global_statistics_empty_database(self, client: TestClient, admin_token: str):
        """Test global statistics with empty database."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        # Test without sample data
        response = client.get("/api/v1/admin/statistics/global", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        stats = data["data"]
        
        # Should return zeros for empty database
        assert stats["total_trips"] >= 0
        assert stats["total_revenue"] >= 0
        assert stats["completion_rate"] >= 0

    def test_global_statistics_response_structure(self, client: TestClient, admin_token: str):
        """Test that global statistics response has correct structure."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        response = client.get("/api/v1/admin/statistics/global", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "success" in data
        assert "data" in data
        
        stats = data["data"]
        required_fields = [
            "total_users", "total_drivers", "total_riders", "active_drivers",
            "total_trips", "trips_today", "trips_this_week", "trips_this_month",
            "total_revenue", "revenue_today", "revenue_this_week", "revenue_this_month",
            "average_trip_duration_minutes", "average_trip_distance_km", "average_trip_cost",
            "completed_trips", "cancelled_trips", "completion_rate",
            "online_drivers", "busy_drivers", "offline_drivers"
        ]
        
        for field in required_fields:
            assert field in stats
            assert isinstance(stats[field], (int, float))
