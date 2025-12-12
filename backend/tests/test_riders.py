"""
Tests for rider API endpoints including trip planning and driver matching.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json

from src.models.user import Driver
from src.models.location import Location


class TestRiderEndpoints:
    """Test cases for rider management endpoints."""

    def test_command_course_success(self, client: TestClient, mock_supabase):
        """Test successful driver matching for trip planning."""
        from src.models.location import Location
        from src.models.user import Driver, User
        
        # Create mock Location object
        mock_location = Mock(spec=Location)
        mock_location.user_id = "driver_user_123"
        mock_location.latitude = 33.8886
        mock_location.longitude = 35.4955
        
        # Create mock Driver object
        mock_driver = Mock(spec=Driver)
        mock_driver.user_id = "driver_user_123"
        mock_driver.taxi_number = "TAXI-123"
        
        # Create mock User object
        mock_user = Mock(spec=User)
        mock_user.id = "driver_user_123"
        mock_user.name = "John Driver"

        with patch('src.services.location.LocationService.get_all_active_drivers') as mock_get_drivers, \
             patch('src.services.location.LocationService.haversine') as mock_haversine, \
             patch('src.db.session.get_session') as mock_get_session:

            # Mock session
            mock_session = Mock()
            mock_get_session.return_value = iter([mock_session])

            # Mock the database queries
            mock_session.exec.return_value.first.side_effect = [mock_driver, mock_user]
            
            # Mock driver locations
            mock_get_drivers.return_value = [mock_location]

            # Mock distance calculation (5km)
            mock_haversine.return_value = 5.0

            response = client.post(
                "/api/v1/riders/command-course",
                json={
                    "rider_lat": 33.8886,
                    "rider_lng": 35.4955,
                    "destination_lat": 33.9200,
                    "destination_lng": 35.5200
                },
                headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["driver_name"] == "John Driver"
            assert data["taxi_number"] == "TAXI-123"
            assert data["total_distance_km"] == 10.0  # 5 + 5
            assert data["rider_to_driver_distance_km"] == 5.0
            assert data["rider_to_destination_distance_km"] == 5.0
            assert data["pickup_cost_usd"] == 2.5  # 5km * 0.5$/km

    def test_command_course_no_drivers(self, client: TestClient):
        """Test when no drivers are available within 10km."""
        with patch('src.services.location.LocationService.get_all_active_drivers') as mock_get_drivers:
            mock_get_drivers.return_value = []

            response = client.post(
                "/api/v1/riders/command-course",
                json={
                    "rider_lat": 33.8886,
                    "rider_lng": 35.4955,
                    "destination_lat": 33.9200,
                    "destination_lng": 35.5200
                },
                headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"}
            )

            assert response.status_code == 404
            data = response.json()
            assert data["success"] is False
            assert "no drivers found" in data["message"].lower()

    def test_command_course_distance_calculation(self, client: TestClient, mock_supabase):
        """Test accurate distance calculations between rider and driver."""
        # Mock driver data
        mock_driver = Mock()
        mock_driver.id = "driver_123"
        mock_driver.name = "John Driver"
        mock_driver.taxi_number = "TAXI-123"
        mock_driver.phone = "+1234567890"

        # Mock location data
        mock_location = Mock()
        mock_location.latitude = 33.8886
        mock_location.longitude = 35.4955

        with patch('src.services.location.LocationService.get_all_active_drivers') as mock_get_drivers, \
             patch('src.services.location.LocationService.haversine') as mock_haversine, \
             patch('src.db.session.get_session') as mock_get_session:

            # Mock session
            mock_session = Mock()
            mock_get_session.return_value = iter([mock_session])

            # Mock driver with location
            mock_driver.location = [mock_location]
            mock_get_drivers.return_value = [mock_driver]

            # Mock specific distances
            def haversine_side_effect(lat1, lon1, lat2, lon2):
                # Rider to driver: 3km
                if lat1 == 33.8886 and lon1 == 35.4955 and lat2 == 33.8886 and lon2 == 35.4955:
                    return 3.0
                # Rider to destination: 7km
                elif lat1 == 33.8886 and lon1 == 35.4955 and lat2 == 33.9200 and lon2 == 35.5200:
                    return 7.0
                return 0.0

            mock_haversine.side_effect = haversine_side_effect

            response = client.post(
                "/api/v1/riders/command-course",
                json={
                    "rider_lat": 33.8886,
                    "rider_lng": 35.4955,
                    "destination_lat": 33.9200,
                    "destination_lng": 35.5200
                },
                headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["rider_to_driver_distance_km"] == 3.0
            assert data["rider_to_destination_distance_km"] == 7.0
            assert data["total_distance_km"] == 10.0  # 3 + 7
            assert data["pickup_cost_usd"] == 1.5  # 3km * 0.5$/km

    def test_command_course_cost_calculation(self, client: TestClient, mock_supabase):
        """Test cost calculation based on distance."""
        # Mock driver data
        mock_driver = Mock()
        mock_driver.id = "driver_123"
        mock_driver.name = "John Driver"
        mock_driver.taxi_number = "TAXI-123"
        mock_driver.phone = "+1234567890"

        # Mock location data
        mock_location = Mock()
        mock_location.latitude = 33.8886
        mock_location.longitude = 35.4955

        with patch('src.services.location.LocationService.get_all_active_drivers') as mock_get_drivers, \
             patch('src.services.location.LocationService.haversine') as mock_haversine, \
             patch('src.db.session.get_session') as mock_get_session:

            # Mock session
            mock_session = Mock()
            mock_get_session.return_value = iter([mock_session])

            # Mock driver with location
            mock_driver.location = [mock_location]
            mock_get_drivers.return_value = [mock_driver]

            # Mock distances for cost calculation
            mock_haversine.return_value = 4.0  # 4km rider to driver
            # For rider to destination, we'll mock it as 6km total

            response = client.post(
                "/api/v1/riders/command-course",
                json={
                    "rider_lat": 33.8886,
                    "rider_lng": 35.4955,
                    "destination_lat": 33.9200,
                    "destination_lng": 35.5200
                },
                headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"}
            )

            assert response.status_code == 200
            data = response.json()

            # Verify cost calculation (rider_to_driver_distance * 0.5)
            expected_total_distance = data["rider_to_driver_distance_km"] + data["rider_to_destination_distance_km"]
            expected_cost = data["rider_to_driver_distance_km"] * 0.5
            assert data["pickup_cost_usd"] == expected_cost

    def test_command_course_10km_filtering(self, client: TestClient, mock_supabase):
        """Test that only drivers within 10km are considered."""
        # Mock two drivers - one within 10km, one outside
        mock_driver_near = Mock()
        mock_driver_near.id = "driver_near"
        mock_driver_near.name = "Near Driver"
        mock_driver_near.taxi_number = "TAXI-NEAR"
        mock_driver_near.phone = "+1234567890"

        mock_driver_far = Mock()
        mock_driver_far.id = "driver_far"
        mock_driver_far.name = "Far Driver"
        mock_driver_far.taxi_number = "TAXI-FAR"
        mock_driver_far.phone = "+1234567891"

        # Mock locations
        mock_location_near = Mock()
        mock_location_near.latitude = 33.8886
        mock_location_near.longitude = 35.4955

        mock_location_far = Mock()
        mock_location_far.latitude = 33.9500  # Far away
        mock_location_far.longitude = 35.5500

        with patch('src.services.location.LocationService.get_all_active_drivers') as mock_get_drivers, \
             patch('src.services.location.LocationService.haversine') as mock_haversine, \
             patch('src.db.session.get_session') as mock_get_session:

            # Mock session
            mock_session = Mock()
            mock_get_session.return_value = iter([mock_session])

            # Mock drivers with locations
            mock_driver_near.location = [mock_location_near]
            mock_driver_far.location = [mock_location_far]
            mock_get_drivers.return_value = [mock_driver_near, mock_driver_far]

            # Mock distance - near driver is 5km, far driver is 15km
            def haversine_side_effect(lat1, lon1, lat2, lon2):
                if lat2 == 33.8886 and lon2 == 35.4955:  # Near driver
                    return 5.0
                elif lat2 == 33.9500 and lon2 == 35.5500:  # Far driver
                    return 15.0
                return 5.0  # Default for rider to destination

            mock_haversine.side_effect = haversine_side_effect

            response = client.post(
                "/api/v1/riders/command-course",
                json={
                    "rider_lat": 33.8886,
                    "rider_lng": 35.4955,
                    "destination_lat": 33.9200,
                    "destination_lng": 35.5200
                },
                headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"}
            )

            assert response.status_code == 200
            data = response.json()

            # Should return the near driver, not the far one
            assert data["driver_name"] == "Near Driver"
            assert data["rider_to_driver_distance_km"] == 5.0

    def test_command_course_validation_error(self, client: TestClient):
        """Test validation errors for invalid coordinates."""
        # Test missing required fields
        response = client.post(
            "/api/v1/riders/command-course",
            json={"rider_lat": 33.8886},  # Missing other required fields
            headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"}
        )

        assert response.status_code == 422  # Validation error

    def test_command_course_invalid_coordinates(self, client: TestClient):
        """Test with invalid coordinate values."""
        response = client.post(
            "/api/v1/riders/command-course",
            json={
                "rider_lat": 91.0,  # Invalid latitude (>90)
                "rider_lng": 35.4955,
                "destination_lat": 33.9200,
                "destination_lng": 35.5200
            },
            headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"}
        )

        assert response.status_code == 422  # Validation error
