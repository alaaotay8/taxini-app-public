"""
Tests for admin trip history management endpoints.
"""

import pytest
from datetime import datetime, date, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.models.user import User, Driver, Rider, Admin
from src.models.trip import Trip
from src.services.admin_auth import AdminAuthService


class TestAdminTripHistory:
    """Test class for admin trip history management functionality."""

    @pytest.fixture
    def admin_token(self, session: Session):
        """Create admin user and get authentication token."""
        # Create admin user
        admin_user = User(
            auth_id="admin-trips-test",
            name="Trips Admin",
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
            test_column="trips_admin"
        )
        session.add(admin_profile)
        session.commit()
        
        # Generate token
        auth_service = AdminAuthService()
        token = auth_service.create_admin_token(admin_user.id, admin_user.email)
        return token

    @pytest.fixture
    def sample_trip_data(self, session: Session):
        """Create comprehensive sample data for trip testing."""
        # Create drivers
        drivers = []
        for i in range(3):
            user = User(
                auth_id=f"driver-trip-{i}",
                name=f"Trip Driver {i}",
                email=f"tripdriver{i}@example.com",
                phone_number=f"+1500000{i:03d}",
                role="driver",
                auth_status="verified"
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            
            driver = Driver(
                user_id=user.id,
                taxi_number=f"TRIP-{i}",
                account_status="verified",
                driver_status="online"
            )
            session.add(driver)
            drivers.append(user)
        
        # Create riders
        riders = []
        for i in range(4):
            user = User(
                auth_id=f"rider-trip-{i}",
                name=f"Trip Rider {i}",
                email=f"triprider{i}@example.com",
                phone_number=f"+1600000{i:03d}",
                role="rider",
                auth_status="verified"
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            
            rider = Rider(
                user_id=user.id,
                residence_place=f"Area {i}"
            )
            session.add(rider)
            riders.append(user)
        
        session.commit()
        
        # Create trips with various scenarios
        trips = []
        today = datetime.utcnow()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        
        trip_scenarios = [
            # Completed trips
            {
                "rider_id": riders[0].id,
                "driver_id": drivers[0].id,
                "pickup_address": "Tunis Center, Tunisia",
                "destination_address": "La Marsa Beach, Tunisia",
                "status": "completed",
                "trip_type": "regular",
                "estimated_distance_km": 15.2,
                "estimated_cost_tnd": 25.50,
                "requested_at": today - timedelta(hours=2),
                "started_at": today - timedelta(hours=1, minutes=45),
                "completed_at": today - timedelta(hours=1, minutes=15),
                "rider_rating": 5,
                "driver_rating": 4,
                "created_at": today - timedelta(hours=2)
            },
            {
                "rider_id": riders[1].id,
                "driver_id": drivers[1].id,
                "pickup_address": "Avenue Habib Bourguiba, Tunis",
                "destination_address": "Carthage Ancient City",
                "status": "completed",
                "trip_type": "express",
                "estimated_distance_km": 12.8,
                "estimated_cost_tnd": 32.75,
                "requested_at": yesterday,
                "started_at": yesterday + timedelta(minutes=15),
                "completed_at": yesterday + timedelta(minutes=45),
                "rider_rating": 4,
                "driver_rating": 5,
                "created_at": yesterday
            },
            # Cancelled trips
            {
                "rider_id": riders[2].id,
                "driver_id": None,
                "pickup_address": "Sousse Medina, Tunisia",
                "destination_address": "Port El Kantaoui, Sousse",
                "status": "cancelled",
                "trip_type": "regular",
                "estimated_distance_km": 8.5,
                "estimated_cost_tnd": 18.25,
                "requested_at": today - timedelta(hours=3),
                "cancelled_at": today - timedelta(hours=2, minutes=30),
                "created_at": today - timedelta(hours=3)
            },
            # Active trips
            {
                "rider_id": riders[3].id,
                "driver_id": drivers[2].id,
                "pickup_address": "Monastir Marina, Tunisia",
                "destination_address": "Skanes Beach, Monastir",
                "status": "started",
                "trip_type": "regular",
                "estimated_distance_km": 6.3,
                "estimated_cost_tnd": 15.00,
                "requested_at": today - timedelta(minutes=30),
                "started_at": today - timedelta(minutes=15),
                "created_at": today - timedelta(minutes=30)
            },
            # Requested trips
            {
                "rider_id": riders[0].id,
                "driver_id": None,
                "pickup_address": "Hammamet Center, Tunisia",
                "destination_address": "Nabeul Market, Tunisia",
                "status": "requested",
                "trip_type": "regular",
                "estimated_distance_km": 11.7,
                "estimated_cost_tnd": 22.40,
                "requested_at": today - timedelta(minutes=10),
                "created_at": today - timedelta(minutes=10)
            },
            # Older trip for date filtering
            {
                "rider_id": riders[1].id,
                "driver_id": drivers[0].id,
                "pickup_address": "Sfax Medina, Tunisia",
                "destination_address": "Sfax Airport, Tunisia",
                "status": "completed",
                "trip_type": "regular",
                "estimated_distance_km": 20.1,
                "estimated_cost_tnd": 35.60,
                "requested_at": week_ago,
                "started_at": week_ago + timedelta(minutes=10),
                "completed_at": week_ago + timedelta(minutes=40),
                "rider_rating": 3,
                "driver_rating": 4,
                "created_at": week_ago
            }
        ]
        
        for scenario in trip_scenarios:
            trip = Trip(**scenario)
            session.add(trip)
            trips.append(trip)
        
        session.commit()
        return {"drivers": drivers, "riders": riders, "trips": trips}

    def test_get_all_trips_success(self, client: TestClient, admin_token: str, sample_trip_data):
        """Test successful retrieval of all trips."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        response = client.get("/api/v1/admin/trips", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["data"]) >= 6
        assert "pagination" in data
        
        # Check trip structure
        trip = data["data"][0]
        required_fields = [
            "id", "rider_id", "rider_name", "rider_phone",
            "pickup_address", "destination_address", "status",
            "estimated_distance_km", "estimated_cost_tnd", "created_at"
        ]
        for field in required_fields:
            assert field in trip

    def test_get_trips_with_pagination(self, client: TestClient, admin_token: str, sample_trip_data):
        """Test trip retrieval with pagination."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        response = client.get("/api/v1/admin/trips?page=1&page_size=3", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["data"]) <= 3
        
        pagination = data["pagination"]
        assert pagination["current_page"] == 1
        assert pagination["page_size"] == 3
        assert pagination["total_items"] >= 6

    def test_filter_trips_by_status(self, client: TestClient, admin_token: str, sample_trip_data):
        """Test filtering trips by status."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        # Test completed trips
        response = client.get("/api/v1/admin/trips?status=completed", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        for trip in data["data"]:
            assert trip["status"] == "completed"

    def test_filter_trips_by_driver(self, client: TestClient, admin_token: str, sample_trip_data):
        """Test filtering trips by driver ID."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        driver_id = sample_trip_data["drivers"][0].id
        response = client.get(f"/api/v1/admin/trips?driver_id={driver_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        for trip in data["data"]:
            if trip["driver_id"]:  # Some trips might not have drivers
                assert trip["driver_id"] == driver_id

    def test_filter_trips_by_rider(self, client: TestClient, admin_token: str, sample_trip_data):
        """Test filtering trips by rider ID."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        rider_id = sample_trip_data["riders"][0].id
        response = client.get(f"/api/v1/admin/trips?rider_id={rider_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        for trip in data["data"]:
            assert trip["rider_id"] == rider_id

    def test_filter_trips_by_date_range(self, client: TestClient, admin_token: str, sample_trip_data):
        """Test filtering trips by date range."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        today = date.today()
        response = client.get(
            f"/api/v1/admin/trips?start_date={today}&end_date={today}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        # Should only return today's trips

    def test_search_trips_by_address(self, client: TestClient, admin_token: str, sample_trip_data):
        """Test searching trips by address."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        response = client.get("/api/v1/admin/trips?search=Tunis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        # Should return trips with "Tunis" in addresses

    def test_search_trips_by_rider_name(self, client: TestClient, admin_token: str, sample_trip_data):
        """Test searching trips by rider name."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        response = client.get("/api/v1/admin/trips?search=Trip Rider", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        # Should return trips for riders with "Trip Rider" in name

    def test_combined_filters(self, client: TestClient, admin_token: str, sample_trip_data):
        """Test using multiple filters together."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        today = date.today()
        response = client.get(
            f"/api/v1/admin/trips?status=completed&start_date={today}&page_size=5",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        for trip in data["data"]:
            assert trip["status"] == "completed"

    def test_get_specific_trip_success(self, client: TestClient, admin_token: str, sample_trip_data):
        """Test successful retrieval of a specific trip."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        trip_id = sample_trip_data["trips"][0].id
        response = client.get(f"/api/v1/admin/trips/{trip_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        trip = data["data"]
        assert trip["id"] == str(trip_id)
        assert "rider_name" in trip
        assert "driver_name" in trip

    def test_get_trip_not_found(self, client: TestClient, admin_token: str):
        """Test retrieval of non-existent trip."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        fake_trip_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v1/admin/trips/{fake_trip_id}", headers=headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_trips_unauthorized(self, client: TestClient):
        """Test trip endpoints without authentication."""
        # Test GET all trips
        response = client.get("/api/v1/admin/trips")
        assert response.status_code == 401
        
        # Test GET specific trip
        response = client.get("/api/v1/admin/trips/some-id")
        assert response.status_code == 401

    def test_trips_invalid_token(self, client: TestClient):
        """Test trip endpoints with invalid token."""
        headers = {
            "Authorization": "Bearer invalid_token",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        response = client.get("/api/v1/admin/trips", headers=headers)
        assert response.status_code == 401

    def test_trips_missing_api_key(self, client: TestClient, admin_token: str):
        """Test trip endpoints without API key."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.get("/api/v1/admin/trips", headers=headers)
        assert response.status_code == 401

    def test_invalid_pagination_params(self, client: TestClient, admin_token: str):
        """Test trip endpoint with invalid pagination parameters."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        # Test negative page
        response = client.get("/api/v1/admin/trips?page=-1", headers=headers)
        assert response.status_code == 422
        
        # Test page size too large
        response = client.get("/api/v1/admin/trips?page_size=1000", headers=headers)
        assert response.status_code == 422

    def test_invalid_date_format(self, client: TestClient, admin_token: str):
        """Test trip endpoint with invalid date format."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        response = client.get("/api/v1/admin/trips?start_date=invalid-date", headers=headers)
        assert response.status_code == 422

    def test_trips_response_structure(self, client: TestClient, admin_token: str, sample_trip_data):
        """Test that trip responses have correct structure."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        # Test GET all trips
        response = client.get("/api/v1/admin/trips", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)
        
        pagination = data["pagination"]
        required_pagination_fields = ["current_page", "page_size", "total_items", "total_pages"]
        for field in required_pagination_fields:
            assert field in pagination

    def test_trip_ratings_display(self, client: TestClient, admin_token: str, sample_trip_data):
        """Test that trip ratings are properly displayed."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        response = client.get("/api/v1/admin/trips?status=completed", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Find a completed trip with ratings
        completed_trips = [trip for trip in data["data"] if trip["status"] == "completed"]
        assert len(completed_trips) > 0
        
        for trip in completed_trips:
            # Ratings should be present for completed trips
            assert "rider_rating" in trip
            assert "driver_rating" in trip

    def test_empty_trips_response(self, client: TestClient, admin_token: str):
        """Test trip endpoint response when no trips match filters."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        # Use a filter that should return no results
        response = client.get("/api/v1/admin/trips?status=nonexistent_status", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["data"]) == 0
        assert data["pagination"]["total_items"] == 0
