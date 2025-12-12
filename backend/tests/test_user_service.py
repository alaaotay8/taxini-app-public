"""
Tests for user service functionality.
"""

import pytest
from sqlmodel import Session
from unittest.mock import patch

from src.services.users import UserService
from src.models.user import User, Driver, Rider, Admin
from src.models.enums import UserRole


class TestUserService:
    """Test cases for UserService class."""

    def test_create_user_profile_driver_success(self, session: Session):
        """Test successful driver profile creation."""
        role_specific_data = {
            "id_card": "https://example.com/id_card.jpg",
            "driver_license": "https://example.com/license.jpg",
            "taxi_number": "TAXI-123",
            "account_status": "locked"
        }
        
        result = UserService.create_user_profile(
            session=session,
            auth_id="test_auth_id",
            name="John Driver",
            email="john@example.com",
            phone_number="+1234567890",
            role=UserRole.DRIVER,
            role_specific_data=role_specific_data
        )
        
        assert result["success"] is True
        assert "User profile created successfully" in result["message"]
        assert "user" in result
        assert "role_profile" in result
        
        # Verify user was created
        user = result["user"]
        assert user.name == "John Driver"
        assert user.role == "driver"
        assert user.auth_status == "verified"
        
        # Verify driver profile was created
        driver = result["role_profile"]
        assert driver.taxi_number == "TAXI-123"
        assert driver.account_status == "locked"

    def test_create_user_profile_rider_success(self, session: Session):
        """Test successful rider profile creation."""
        role_specific_data = {
            "residence_place": "Downtown"
        }
        
        result = UserService.create_user_profile(
            session=session,
            auth_id="test_auth_id",
            name="Jane Rider",
            email="jane@example.com",
            phone_number="+1234567890",
            role=UserRole.RIDER,
            role_specific_data=role_specific_data
        )
        
        assert result["success"] is True
        rider = result["role_profile"]
        assert rider.residence_place == "Downtown"

    def test_create_user_profile_duplicate_driver(self, session: Session):
        """Test duplicate driver profile creation."""
        # Create first driver
        UserService.create_user_profile(
            session=session,
            auth_id="test_auth_id",
            name="John Driver",
            email="john@example.com",
            phone_number="+1234567890",
            role=UserRole.DRIVER,
            role_specific_data={"taxi_number": "TAXI-123"}
        )
        
        # Try to create duplicate
        result = UserService.create_user_profile(
            session=session,
            auth_id="test_auth_id",
            name="John Driver 2",
            email="john2@example.com",
            phone_number="+1234567890",
            role=UserRole.DRIVER,
            role_specific_data={"taxi_number": "TAXI-456"}
        )
        
        assert result["success"] is False
        assert "already associated with a driver profile" in result["message"]

    def test_create_user_profile_admin_not_allowed(self, session: Session):
        """Test that admin profile creation is not allowed."""
        result = UserService.create_user_profile(
            session=session,
            auth_id="test_auth_id",
            name="Admin User",
            email="admin@example.com",
            phone_number="+1234567890",
            role=UserRole.ADMIN,
            role_specific_data={}
        )
        
        assert result["success"] is False
        assert "Admin profiles cannot be created" in result["message"]

    def test_get_user_by_auth_id_success(self, session: Session):
        """Test successful user retrieval by auth ID."""
        # Create a user first
        UserService.create_user_profile(
            session=session,
            auth_id="test_auth_id",
            name="Test User",
            email="test@example.com",
            phone_number="+1234567890",
            role=UserRole.RIDER,
            role_specific_data={"residence_place": "Downtown"}
        )
        
        user = UserService.get_user_by_auth_id(session, "test_auth_id")
        
        assert user is not None
        assert user.name == "Test User"
        assert user.auth_id == "test_auth_id"

    def test_get_user_by_auth_id_not_found(self, session: Session):
        """Test user retrieval with non-existent auth ID."""
        user = UserService.get_user_by_auth_id(session, "non_existent_auth_id")
        assert user is None

    def test_get_user_with_role_profile_driver(self, session: Session):
        """Test getting user with driver role profile."""
        # Create driver
        create_result = UserService.create_user_profile(
            session=session,
            auth_id="test_auth_id",
            name="John Driver",
            email="john@example.com",
            phone_number="+1234567890",
            role=UserRole.DRIVER,
            role_specific_data={"taxi_number": "TAXI-123"}
        )
        
        user_id = create_result["user"].id
        
        result = UserService.get_user_with_role_profile(session, user_id)
        
        assert result["success"] is True
        assert result["user"].role == "driver"
        assert result["role_profile"] is not None
        assert result["role_profile"].taxi_number == "TAXI-123"

    def test_get_user_with_role_profile_not_found(self, session: Session):
        """Test getting non-existent user with role profile."""
        result = UserService.get_user_with_role_profile(session, "non_existent_id")
        
        assert result["success"] is False
        assert "User not found" in result["message"]

    def test_update_user_profile_success(self, session: Session):
        """Test successful user profile update."""
        # Create user first
        create_result = UserService.create_user_profile(
            session=session,
            auth_id="test_auth_id",
            name="John Driver",
            email="john@example.com",
            phone_number="+1234567890",
            role=UserRole.DRIVER,
            role_specific_data={"taxi_number": "TAXI-123"}
        )
        
        user_id = create_result["user"].id
        
        # Update user
        user_data = {"name": "John Updated Driver"}
        role_data = {"taxi_number": "TAXI-456"}
        
        result = UserService.update_user_profile(
            session=session,
            user_id=user_id,
            user_data=user_data,
            role_data=role_data
        )
        
        assert result["success"] is True
        assert result["user"].name == "John Updated Driver"

    def test_get_user_profiles_by_auth_id_multiple(self, session: Session):
        """Test getting multiple profiles for same auth ID."""
        auth_id = "test_auth_id"
        
        # Create driver profile
        UserService.create_user_profile(
            session=session,
            auth_id=auth_id,
            name="John Driver",
            email="john@example.com",
            phone_number="+1234567890",
            role=UserRole.DRIVER,
            role_specific_data={"taxi_number": "TAXI-123"}
        )
        
        # Create rider profile with different auth_id to test multiple
        UserService.create_user_profile(
            session=session,
            auth_id="different_auth_id",
            name="Jane Rider",
            email="jane@example.com",
            phone_number="+1987654321",
            role=UserRole.RIDER,
            role_specific_data={"residence_place": "Downtown"}
        )
        
        result = UserService.get_all_user_profiles_with_data(session, auth_id)
        
        assert result["success"] is True
        assert result["total_profiles"] == 1
        assert len(result["profiles"]) == 1
        assert result["profiles"][0]["role"] == "driver"

    def test_get_user_profiles_by_auth_id_none(self, session: Session):
        """Test getting profiles for non-existent auth ID."""
        result = UserService.get_all_user_profiles_with_data(session, "non_existent_auth_id")
        
        assert result["success"] is True
        assert result["total_profiles"] == 0
        assert len(result["profiles"]) == 0
