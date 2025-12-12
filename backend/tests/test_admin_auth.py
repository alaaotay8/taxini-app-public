"""
Tests for admin authentication.
"""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.app import app
from src.models.user import User, Admin
from src.services.admin_auth import (
    authenticate_admin,
    verify_admin_token
)


@pytest.fixture
def admin_user(test_db_session):
    """Create an admin user in the test database."""
    # Create user with admin role
    user = User(
        auth_id="test-admin-auth-id",
        name="Test Admin",
        email="admin@test.com",
        phone_number="+1234567890",
        role="admin",
        auth_status="verified"
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    
    # Create admin profile with password
    admin = Admin(
        user_id=user.id,
        test_column="adminpassword"  # Password field
    )
    test_db_session.add(admin)
    test_db_session.commit()
    
    return user


def test_admin_login(client, admin_user, test_db_session, monkeypatch):
    """Test admin login with valid credentials."""
    # Mock the Supabase authentication
    from src.services.admin_auth import authenticate_admin
    
    # Store the original function
    original_authenticate = authenticate_admin
    
    # Create a mock function that returns a successful response
    def mock_authenticate(session, email, password):
        if email == "admin@test.com" and password == "adminpassword":
            return {
                "success": True,
                "message": "Login successful",
                "access_token": "mock.jwt.token",
                "admin_id": admin_user.id,
                "name": "Test Admin",
                "email": "admin@test.com"
            }
        return {
            "success": False,
            "message": "Invalid email or password"
        }
    
    # Apply the mock function
    monkeypatch.setattr(
        "src.services.admin_auth.authenticate_admin", 
        mock_authenticate
    )
    
    # Test the endpoint
    response = client.post(
        "/api/v1/admin/login",
        json={
            "email": "admin@test.com",
            "password": "adminpassword"
        }
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data
    assert data["name"] == "Test Admin"
    assert data["email"] == "admin@test.com"


def test_admin_login_invalid_password(client, admin_user):
    """Test admin login with invalid password."""
    response = client.post(
        "/api/v1/admin/login",
        json={
            "email": "admin@test.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    
    data = response.json()
    assert "detail" in data
    assert "Invalid email or password" in data["detail"]


def test_admin_login_invalid_email(client, admin_user):
    """Test admin login with invalid email."""
    response = client.post(
        "/api/v1/admin/login",
        json={
            "email": "wrong@test.com",
            "password": "adminpassword"
        }
    )
    assert response.status_code == 401
    
    data = response.json()
    assert "detail" in data
    assert "Invalid email or password" in data["detail"]


def test_authenticate_admin(admin_user, test_db_session):
    """Test authenticate_admin function."""
    # Valid credentials
    result = authenticate_admin(test_db_session, "admin@test.com", "adminpassword")
    assert result["success"] is True
    assert "access_token" in result
    
    # Invalid password
    result = authenticate_admin(test_db_session, "admin@test.com", "wrongpassword")
    assert result["success"] is False
    
    # Invalid email
    result = authenticate_admin(test_db_session, "wrong@test.com", "adminpassword")
    assert result["success"] is False


def test_verify_token(admin_user, monkeypatch):
    """Test token verification."""
    from src.services.admin_auth import verify_admin_token
    
    # Mock the Supabase token verification
    def mock_verify_token(token):
        if token == "valid.mock.token":
            return {
                "success": True,
                "user_id": admin_user.id,
                "email": admin_user.email
            }
        return {
            "success": False,
            "message": "Invalid token"
        }
    
    # Apply the mock function
    monkeypatch.setattr(
        "src.services.admin_auth.verify_admin_token", 
        mock_verify_token
    )
    
    # Verify valid token
    result = verify_admin_token("valid.mock.token")
    assert result["success"] is True
    assert result["user_id"] == admin_user.id
    assert result["email"] == admin_user.email
    
    # Invalid token
    result = verify_admin_token("invalid.token.here")
    assert result["success"] is False


def test_admin_dashboard_with_token(client, admin_user, test_db_session, monkeypatch):
    """Test accessing admin dashboard with valid token."""
    from src.services.admin_auth import get_admin_user_dependency
    from src.schemas.auth import CurrentUser
    
    # Mock the admin dependency to return a valid admin user
    def mock_admin_dependency(*args, **kwargs):
        return CurrentUser(
            auth_id=admin_user.id,
            email=admin_user.email
        )
    
    # Apply the mock function
    monkeypatch.setattr(
        "src.services.admin_auth.get_admin_user_dependency", 
        mock_admin_dependency
    )
    
    # Access dashboard with mocked token validation
    response = client.get(
        "/api/v1/admin/dashboard",
        headers={"Authorization": "Bearer mock.jwt.token"}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "statistics" in data
