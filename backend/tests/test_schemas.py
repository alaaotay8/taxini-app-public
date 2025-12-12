"""
Tests for Pydantic schemas and validation.
"""

import pytest
from pydantic import ValidationError
from pydantic import HttpUrl
from datetime import datetime

from src.schemas.user import (
    CompleteProfileRequest,
    DriverProfileData,
    RiderProfileData,
    UpdateProfileRequest,
    UserResponse
)
from src.schemas.ticket import (
    TicketCreateRequest,
    TicketUpdateRequest,
    AdminTicketUpdateRequest,
    TicketResponse,
    AdminTicketResponse,
    TicketStatsResponse
)
from src.models.enums import UserRole
from src.models.ticket import TicketStatus, TicketPriority


class TestDriverProfileData:
    """Test cases for DriverProfileData schema."""

    def test_valid_driver_profile_data(self):
        """Test valid driver profile data."""
        data = {
            "id_card": "https://example.com/id_card.jpg",
            "driver_license": "https://example.com/license.jpg",
            "taxi_number": "TAXI-123",
            "account_status": "locked"
        }
        
        profile = DriverProfileData(**data)
        
        assert str(profile.id_card) == "https://example.com/id_card.jpg"
        assert str(profile.driver_license) == "https://example.com/license.jpg"
        assert profile.taxi_number == "TAXI-123"
        assert profile.account_status == "locked"

    def test_invalid_url_validation(self):
        """Test that invalid URLs are rejected."""
        data = {
            "id_card": "not-a-valid-url",
            "driver_license": "https://example.com/license.jpg",
            "taxi_number": "TAXI-123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            DriverProfileData(**data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"][-1] == "id_card" for error in errors)

    def test_missing_required_fields(self):
        """Test that required fields are validated."""
        data = {
            "id_card": "https://example.com/id_card.jpg"
            # Missing driver_license and taxi_number
        }
        
        with pytest.raises(ValidationError) as exc_info:
            DriverProfileData(**data)
        
        errors = exc_info.value.errors()
        field_names = [error["loc"][-1] for error in errors]
        assert "driver_license" in field_names
        assert "taxi_number" in field_names

    def test_account_status_validation(self):
        """Test account status validation."""
        valid_data = {
            "id_card": "https://example.com/id_card.jpg",
            "driver_license": "https://example.com/license.jpg",
            "taxi_number": "TAXI-123",
            "account_status": "verified"
        }
        
        profile = DriverProfileData(**valid_data)
        assert profile.account_status == "verified"
        
        # Test invalid status
        invalid_data = valid_data.copy()
        invalid_data["account_status"] = "invalid_status"
        
        with pytest.raises(ValidationError):
            DriverProfileData(**invalid_data)

    def test_default_account_status(self):
        """Test default account status."""
        data = {
            "id_card": "https://example.com/id_card.jpg",
            "driver_license": "https://example.com/license.jpg",
            "taxi_number": "TAXI-123"
        }
        
        profile = DriverProfileData(**data)
        assert profile.account_status == "locked"

    def test_taxi_number_length_validation(self):
        """Test taxi number length validation."""
        data = {
            "id_card": "https://example.com/id_card.jpg",
            "driver_license": "https://example.com/license.jpg",
            "taxi_number": "x" * 100,  # Too long
            "account_status": "locked"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            DriverProfileData(**data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"][-1] == "taxi_number" for error in errors)


class TestRiderProfileData:
    """Test cases for RiderProfileData schema."""

    def test_valid_rider_profile_data(self):
        """Test valid rider profile data."""
        data = {
            "residence_place": "Downtown City"
        }
        
        profile = RiderProfileData(**data)
        assert profile.residence_place == "Downtown City"

    def test_missing_residence_place(self):
        """Test that residence_place is required."""
        with pytest.raises(ValidationError) as exc_info:
            RiderProfileData()
        
        errors = exc_info.value.errors()
        assert any(error["loc"][-1] == "residence_place" for error in errors)

    def test_residence_place_length_validation(self):
        """Test residence place length validation."""
        data = {
            "residence_place": "x" * 300  # Too long
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RiderProfileData(**data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"][-1] == "residence_place" for error in errors)


class TestCompleteProfileRequest:
    """Test cases for CompleteProfileRequest schema."""

    def test_valid_complete_profile_request_driver(self):
        """Test valid complete profile request for driver."""
        data = {
            "name": "John Driver",
            "email": "john@example.com",
            "role": UserRole.DRIVER,
            "role_specific_data": {
                "id_card": "https://example.com/id_card.jpg",
                "driver_license": "https://example.com/license.jpg",
                "taxi_number": "TAXI-123"
            }
        }
        
        request = CompleteProfileRequest(**data)
        assert request.name == "John Driver"
        assert request.role == UserRole.DRIVER

    def test_valid_complete_profile_request_rider(self):
        """Test valid complete profile request for rider."""
        data = {
            "name": "Jane Rider",
            "email": "jane@example.com",
            "role": UserRole.RIDER,
            "role_specific_data": {
                "residence_place": "Downtown"
            }
        }
        
        request = CompleteProfileRequest(**data)
        assert request.name == "Jane Rider"
        assert request.role == UserRole.RIDER

    def test_invalid_email_format(self):
        """Test invalid email format validation."""
        data = {
            "name": "John Driver",
            "email": "invalid-email",
            "role": UserRole.DRIVER
        }
        
        with pytest.raises(ValidationError) as exc_info:
            CompleteProfileRequest(**data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"][-1] == "email" for error in errors)

    def test_admin_role_validation(self):
        """Test that admin role is rejected."""
        data = {
            "name": "Admin User",
            "email": "admin@example.com",
            "role": UserRole.ADMIN
        }
        
        with pytest.raises(ValidationError) as exc_info:
            CompleteProfileRequest(**data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"][-1] == "role" for error in errors)

    def test_name_length_validation(self):
        """Test name length validation."""
        # Too short
        data = {
            "name": "J",
            "email": "john@example.com",
            "role": UserRole.DRIVER
        }
        
        with pytest.raises(ValidationError):
            CompleteProfileRequest(**data)
        
        # Too long
        data["name"] = "x" * 200
        
        with pytest.raises(ValidationError):
            CompleteProfileRequest(**data)


class TestUpdateProfileRequest:
    """Test cases for UpdateProfileRequest schema."""

    def test_valid_update_request(self):
        """Test valid update profile request."""
        data = {
            "name": "Updated Name",
            "email": "updated@example.com",
            "role_specific_data": {
                "taxi_number": "TAXI-456"
            }
        }
        
        request = UpdateProfileRequest(**data)
        assert request.name == "Updated Name"
        assert request.email == "updated@example.com"

    def test_partial_update_request(self):
        """Test partial update request."""
        data = {
            "name": "Updated Name"
            # Only updating name
        }
        
        request = UpdateProfileRequest(**data)
        assert request.name == "Updated Name"
        assert request.email is None

    def test_empty_update_request(self):
        """Test empty update request."""
        request = UpdateProfileRequest()
        assert request.name is None
        assert request.email is None
        assert request.role_specific_data is None


class TestUserResponse:
    """Test cases for UserResponse schema."""

    def test_valid_user_response(self):
        """Test valid user response schema."""
        data = {
            "id": "user-123",
            "auth_id": "auth-456",
            "name": "John Driver",
            "email": "john@example.com",
            "phone_number": "+1234567890",
            "role": UserRole.DRIVER,
            "auth_status": "verified",
            "created_at": "2025-08-14T12:00:00Z",
            "updated_at": "2025-08-14T12:30:00Z"
        }
        
        response = UserResponse(**data)
        assert response.id == "user-123"
        assert response.name == "John Driver"
        assert response.role == UserRole.DRIVER

    def test_user_response_with_null_updated_at(self):
        """Test user response with null updated_at."""
        data = {
            "id": "user-123",
            "auth_id": "auth-456",
            "name": "John Driver",
            "email": "john@example.com",
            "phone_number": "+1234567890",
            "role": UserRole.DRIVER,
            "auth_status": "verified",
            "created_at": "2025-08-14T12:00:00Z",
            "updated_at": None
        }
        
        response = UserResponse(**data)
        assert response.updated_at is None


class TestHttpUrlValidation:
    """Test cases for HttpUrl validation in schemas."""

    def test_valid_https_url(self):
        """Test valid HTTPS URL."""
        data = {
            "id_card": "https://example.com/id_card.jpg",
            "driver_license": "https://example.com/license.jpg",
            "taxi_number": "TAXI-123"
        }
        
        profile = DriverProfileData(**data)
        assert isinstance(profile.id_card, HttpUrl)

    def test_valid_http_url(self):
        """Test valid HTTP URL."""
        data = {
            "id_card": "http://example.com/id_card.jpg",
            "driver_license": "http://example.com/license.jpg",
            "taxi_number": "TAXI-123"
        }
        
        profile = DriverProfileData(**data)
        assert isinstance(profile.id_card, HttpUrl)

    def test_invalid_url_formats(self):
        """Test various invalid URL formats."""
        invalid_urls = [
            "not-a-url",
            "ftp://example.com/file.jpg",  # Wrong protocol
            "//example.com/file.jpg",  # Missing protocol
            "example.com/file.jpg",  # Missing protocol
            "",  # Empty string
            "javascript:alert('xss')"  # Dangerous URL
        ]


class TestTicketSchemas:
    """Test cases for Ticket schemas."""

    def test_ticket_create_request_validation(self):
        """Test validation for TicketCreateRequest schema."""
        # Valid data
        valid_data = {
            "title": "Test Ticket Title",
            "content": "This is a detailed description of the issue",
            "priority": "high"
        }
        
        ticket_request = TicketCreateRequest(**valid_data)
        assert ticket_request.title == valid_data["title"]
        assert ticket_request.content == valid_data["content"]
        assert ticket_request.priority == TicketPriority.HIGH
        
        # Invalid data - title too short
        with pytest.raises(ValidationError) as exc_info:
            TicketCreateRequest(title="Hi", content="Content is long enough", priority="medium")
        
        errors = exc_info.value.errors()
        assert any("title" in error["loc"] for error in errors)
        
        # Invalid data - content too short
        with pytest.raises(ValidationError) as exc_info:
            TicketCreateRequest(title="Title is long enough", content="Short", priority="medium")
        
        errors = exc_info.value.errors()
        assert any("content" in error["loc"] for error in errors)
        
        # Invalid data - invalid priority enum
        with pytest.raises(ValidationError) as exc_info:
            TicketCreateRequest(
                title="Valid Title", 
                content="Content is long enough", 
                priority="invalid_priority"
            )
        
        errors = exc_info.value.errors()
        assert any("priority" in error["loc"] for error in errors)
    
    def test_ticket_update_request_validation(self):
        """Test validation for TicketUpdateRequest schema."""
        # Valid data
        valid_data = {
            "title": "Updated Title",
            "content": "Updated content with sufficient length",
            "priority": "urgent"
        }
        
        update_request = TicketUpdateRequest(**valid_data)
        assert update_request.title == valid_data["title"]
        assert update_request.content == valid_data["content"]
        assert update_request.priority == TicketPriority.URGENT
        
        # Empty request should be valid (nothing to update)
        empty_request = TicketUpdateRequest()
        assert empty_request.title is None
        assert empty_request.content is None
        assert empty_request.priority is None
        
        # Invalid title length
        with pytest.raises(ValidationError) as exc_info:
            TicketUpdateRequest(title="Hi")
        
        errors = exc_info.value.errors()
        assert any("title" in error["loc"] for error in errors)
    
    def test_admin_ticket_update_request_validation(self):
        """Test validation for AdminTicketUpdateRequest schema."""
        # Valid data
        valid_data = {
            "status": "in_progress",
            "priority": "high",
            "admin_notes": "Working on resolving this issue"
        }
        
        admin_update = AdminTicketUpdateRequest(**valid_data)
        assert admin_update.status == TicketStatus.IN_PROGRESS
        assert admin_update.priority == TicketPriority.HIGH
        assert admin_update.admin_notes == valid_data["admin_notes"]
        
        # Empty request should be valid (nothing to update)
        empty_request = AdminTicketUpdateRequest()
        assert empty_request.status is None
        assert empty_request.priority is None
        assert empty_request.admin_notes is None
        
        # Invalid status enum
        with pytest.raises(ValidationError) as exc_info:
            AdminTicketUpdateRequest(status="invalid_status")
        
        errors = exc_info.value.errors()
        assert any("status" in error["loc"] for error in errors)
    
    def test_ticket_response_schema(self):
        """Test TicketResponse schema."""
        ticket_data = {
            "id": "test-id-123",
            "title": "Test Ticket",
            "content": "This is a test ticket content",
            "user_id": "user-123",
            "user_role": "rider",
            "status": "open",
            "priority": "medium",
            "created_at": datetime.utcnow(),
            "updated_at": None,
            "resolved_at": None,
            "resolved_by": None,
            "issue_at": None
        }
        
        response = TicketResponse(**ticket_data)
        assert response.id == ticket_data["id"]
        assert response.title == ticket_data["title"]
        assert response.user_id == ticket_data["user_id"]
        assert response.status == TicketStatus.OPEN
        assert response.priority == TicketPriority.MEDIUM
        
    def test_admin_ticket_response_schema(self):
        """Test AdminTicketResponse schema."""
        admin_ticket_data = {
            "id": "test-id-123",
            "title": "Test Ticket",
            "content": "This is a test ticket content",
            "user_id": "user-123",
            "user_role": "rider",
            "status": "resolved",
            "priority": "high",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "resolved_at": datetime.utcnow(),
            "resolved_by": "admin-123",
            "admin_notes": "This issue has been resolved",
            "user_name": "John Doe",
            "user_email": "john@example.com",
            "user_phone": "+1234567890"
        }
        
        response = AdminTicketResponse(**admin_ticket_data)
        assert response.id == admin_ticket_data["id"]
        assert response.title == admin_ticket_data["title"]
        assert response.admin_notes == admin_ticket_data["admin_notes"]
        assert response.user_name == admin_ticket_data["user_name"]
        assert response.user_email == admin_ticket_data["user_email"]
        
    def test_ticket_stats_response_schema(self):
        """Test TicketStatsResponse schema."""
        stats_data = {
            "total": 100,
            "open": 50,
            "in_progress": 25,
            "resolved": 15,
            "closed": 10,
            "high_priority": 30,
            "urgent_priority": 10
        }
        
        stats = TicketStatsResponse(**stats_data)
        assert stats.total == stats_data["total"]
        assert stats.open == stats_data["open"]
        assert stats.in_progress == stats_data["in_progress"]
        assert stats.resolved == stats_data["resolved"]
        assert stats.closed == stats_data["closed"]
        assert stats.high_priority == stats_data["high_priority"]
        assert stats.urgent_priority == stats_data["urgent_priority"]
        for invalid_url in invalid_urls:
            data = {
                "id_card": invalid_url,
                "driver_license": "https://example.com/license.jpg",
                "taxi_number": "TAXI-123"
            }
            
            with pytest.raises(ValidationError):
                DriverProfileData(**data)
