"""
Test complete trip notification flow with unified GPS/Trip channels.

This test validates the complete workflow:
1. Driver starts GPS streaming (creates unified channel)
2. Rider creates trip request
3. Trip is assigned to streaming driver
4. Driver receives notification via GPS channel
5. Driver accepts/rejects trip
6. Rider receives response notification
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch
from datetime import datetime
from sqlmodel import Session
from fastapi.testclient import TestClient

from src.app import app
from src.models.user import User, Driver
from src.models.trip import Trip, TripStatus
from src.services.trip import TripService
from src.services.notification import NotificationService
from src.services.realtime_location import RealtimeLocationService
from src.db.session import get_session
from tests.conftest import test_session


class TestTripNotificationFlow:
    """Test the complete trip notification flow."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_driver(self, test_session: Session):
        """Create a mock driver."""
        driver = Driver(
            id="driver_123",
            name="Ahmed Hassan",
            email="ahmed@test.com",
            phone="+216 20 123 456",
            taxi_number="TUN-1234",
            license_number="LIC123456",
            is_active=True,
            is_available=True,
            current_latitude=36.8065,  # Tunis center
            current_longitude=10.1815
        )
        test_session.add(driver)
        test_session.commit()
        test_session.refresh(driver)
        return driver
    
    @pytest.fixture
    def mock_rider(self, test_session: Session):
        """Create a mock rider."""
        rider = User(
            id="rider_456",
            name="Fatma Ben Ali",
            email="fatma@test.com", 
            phone="+216 25 654 321",
            user_type="rider"
        )
        test_session.add(rider)
        test_session.commit()
        test_session.refresh(rider)
        return rider
    
    @pytest.mark.asyncio
    async def test_complete_trip_flow_acceptance(self, test_session: Session, mock_driver: Driver, mock_rider: User):
        """Test complete flow where driver accepts trip."""
        
        # Mock the RealtimeLocationService to simulate active streaming
        with patch.object(RealtimeLocationService, '_active_streams', {mock_driver.id: {
            "driver": mock_driver,
            "channel": Mock(),
            "last_update": datetime.utcnow(),
            "streaming_duration": 0
        }}):
            with patch.object(RealtimeLocationService, 'send_message_to_driver_channel') as mock_send_message:
                mock_send_message.return_value = True
                
                # Step 1: Create trip request
                trip_details = {
                    "pickup_latitude": 36.8065,
                    "pickup_longitude": 10.1815,
                    "pickup_address": "Avenue Habib Bourguiba, Tunis",
                    "destination_latitude": 36.8189,
                    "destination_longitude": 10.1658,
                    "destination_address": "Aéroport Tunis-Carthage",
                    "passenger_count": 2,
                    "notes": "Test trip - urgent"
                }
                
                trip = await TripService.create_trip_request(
                    session=test_session,
                    rider_id=mock_rider.id,
                    **trip_details
                )
                
                assert trip is not None
                assert trip.status == TripStatus.PENDING
                assert trip.rider_id == mock_rider.id
                
                # Step 2: Assign to nearest driver (our mock driver)
                assignment_result = await TripService.assign_nearest_driver(
                    session=test_session,
                    trip_id=trip.id,
                    max_distance_km=10.0
                )
                
                assert assignment_result["success"] is True
                assert assignment_result["driver_id"] == mock_driver.id
                
                # Verify notification was sent via GPS channel
                mock_send_message.assert_called_once()
                call_args = mock_send_message.call_args
                assert call_args[0][0] == mock_driver.id  # driver_id
                
                notification_data = call_args[0][1]  # message
                assert notification_data["type"] == "trip_request"
                assert notification_data["trip_id"] == trip.id
                assert "pickup_address" in notification_data
                assert "destination_address" in notification_data
                
                # Verify trip status updated
                test_session.refresh(trip)
                assert trip.status == TripStatus.ASSIGNED
                assert trip.driver_id == mock_driver.id
                
                # Step 3: Driver accepts trip
                acceptance_result = await TripService.handle_driver_acceptance(
                    session=test_session,
                    driver_id=mock_driver.id,
                    trip_id=trip.id,
                    estimated_arrival=5  # 5 minutes
                )
                
                assert acceptance_result["success"] is True
                assert acceptance_result["status"] == "accepted"
                
                # Verify trip status updated
                test_session.refresh(trip)
                assert trip.status == TripStatus.ACCEPTED
                assert trip.estimated_arrival_minutes == 5
                
                # Verify pending notification was cleaned up
                pending = NotificationService.get_pending_notifications()
                assert mock_driver.id not in pending
    
    @pytest.mark.asyncio
    async def test_complete_trip_flow_rejection(self, test_session: Session, mock_driver: Driver, mock_rider: User):
        """Test complete flow where driver rejects trip."""
        
        with patch.object(RealtimeLocationService, '_active_streams', {mock_driver.id: {
            "driver": mock_driver,
            "channel": Mock(),
            "last_update": datetime.utcnow(),
            "streaming_duration": 0
        }}):
            with patch.object(RealtimeLocationService, 'send_message_to_driver_channel') as mock_send_message:
                mock_send_message.return_value = True
                
                # Create and assign trip
                trip_details = {
                    "pickup_latitude": 36.8065,
                    "pickup_longitude": 10.1815,
                    "pickup_address": "Avenue Habib Bourguiba, Tunis",
                    "destination_latitude": 36.8189,
                    "destination_longitude": 10.1658,
                    "destination_address": "Aéroport Tunis-Carthage",
                    "passenger_count": 1
                }
                
                trip = await TripService.create_trip_request(
                    session=test_session,
                    rider_id=mock_rider.id,
                    **trip_details
                )
                
                await TripService.assign_nearest_driver(
                    session=test_session,
                    trip_id=trip.id,
                    max_distance_km=10.0
                )
                
                # Driver rejects trip
                rejection_result = await TripService.handle_driver_rejection(
                    session=test_session,
                    driver_id=mock_driver.id,
                    trip_id=trip.id,
                    notes="Traffic is too heavy"
                )
                
                assert rejection_result["success"] is True
                assert rejection_result["status"] == "rejected"
                
                # Verify trip status updated
                test_session.refresh(trip)
                assert trip.status == TripStatus.REJECTED
                assert "Traffic is too heavy" in trip.notes
                
                # Verify pending notification was cleaned up
                pending = NotificationService.get_pending_notifications()
                assert mock_driver.id not in pending
    
    @pytest.mark.asyncio
    async def test_auto_rejection_timeout(self, test_session: Session, mock_driver: Driver, mock_rider: User):
        """Test auto-rejection when driver doesn't respond."""
        
        with patch.object(RealtimeLocationService, '_active_streams', {mock_driver.id: {
            "driver": mock_driver,
            "channel": Mock(),
            "last_update": datetime.utcnow(),
            "streaming_duration": 0
        }}):
            with patch.object(RealtimeLocationService, 'send_message_to_driver_channel') as mock_send_message:
                mock_send_message.return_value = True
                
                # Patch timeout to be very short for testing
                with patch.object(NotificationService, 'NOTIFICATION_TIMEOUT', 0.1):  # 0.1 seconds
                    
                    # Create and assign trip
                    trip_details = {
                        "pickup_latitude": 36.8065,
                        "pickup_longitude": 10.1815,
                        "pickup_address": "Test pickup",
                        "destination_latitude": 36.8189,
                        "destination_longitude": 10.1658,
                        "destination_address": "Test destination",
                        "passenger_count": 1
                    }
                    
                    trip = await TripService.create_trip_request(
                        session=test_session,
                        rider_id=mock_rider.id,
                        **trip_details
                    )
                    
                    await TripService.assign_nearest_driver(
                        session=test_session,
                        trip_id=trip.id,
                        max_distance_km=10.0
                    )
                    
                    # Wait for auto-rejection timeout
                    await asyncio.sleep(0.2)  # Wait a bit longer than timeout
                    
                    # Verify trip was auto-rejected
                    test_session.refresh(trip)
                    assert trip.status == TripStatus.REJECTED
                    assert "Auto-rejected due to timeout" in trip.notes
                    
                    # Verify pending notification was cleaned up
                    pending = NotificationService.get_pending_notifications()
                    assert mock_driver.id not in pending
    
    @pytest.mark.asyncio
    async def test_driver_not_streaming(self, test_session: Session, mock_driver: Driver, mock_rider: User):
        """Test notification when driver is not actively streaming GPS."""
        
        # No active streams - driver not streaming
        with patch.object(RealtimeLocationService, '_active_streams', {}):
            
            trip_details = {
                "pickup_latitude": 36.8065,
                "pickup_longitude": 10.1815,
                "pickup_address": "Test pickup",
                "destination_latitude": 36.8189,
                "destination_longitude": 10.1658,
                "destination_address": "Test destination",
                "passenger_count": 1
            }
            
            trip = await TripService.create_trip_request(
                session=test_session,
                rider_id=mock_rider.id,
                **trip_details
            )
            
            # Try to assign to driver who is not streaming
            assignment_result = await TripService.assign_nearest_driver(
                session=test_session,
                trip_id=trip.id,
                max_distance_km=10.0
            )
            
            # Should fail because driver is not actively streaming
            assert assignment_result["success"] is False
            assert "No active streaming drivers found" in assignment_result["message"]
    
    @pytest.mark.asyncio
    async def test_broadcast_system_message(self, test_session: Session, mock_driver: Driver):
        """Test broadcasting system messages to all active drivers."""
        
        mock_channel = Mock()
        with patch.object(RealtimeLocationService, '_active_streams', {mock_driver.id: {
            "driver": mock_driver,
            "channel": mock_channel,
            "last_update": datetime.utcnow(),
            "streaming_duration": 0
        }}):
            with patch.object(RealtimeLocationService, 'send_message_to_driver_channel') as mock_send_message:
                mock_send_message.return_value = True
                
                # Broadcast system message
                await NotificationService.broadcast_system_message(
                    message="System maintenance in 10 minutes",
                    message_type="warning"
                )
                
                # Verify message was sent to active driver
                mock_send_message.assert_called_once()
                call_args = mock_send_message.call_args
                assert call_args[0][0] == mock_driver.id
                
                message_data = call_args[0][1]
                assert message_data["type"] == "system_message"
                assert message_data["message"] == "System maintenance in 10 minutes"
                assert message_data["message_type"] == "warning"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
