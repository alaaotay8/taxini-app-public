"""
Test for password reset functionality.
"""

import pytest
from unittest.mock import MagicMock, patch, ANY
from starlette.testclient import TestClient
from src.app import app


class TestPasswordReset:
    """Test password reset functionality."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture 
    def mock_session(self):
        """Mock database session."""
        mock = MagicMock()
        with patch('src.api.v1.users.get_session') as mock_get_session:
            mock_get_session.return_value = iter([mock])
            yield mock

    def test_reset_password_success(self, client: TestClient, mock_session):
        """Test successful password reset."""
        
        # Mock UserService.get_email_by_phone to return an email
        with patch('src.services.users.UserService.get_email_by_phone') as mock_get_email:
            mock_get_email.return_value = "test@example.com"
            
            # Mock AuthService.reset_password to return success
            with patch('src.services.auth.AuthService.reset_password') as mock_reset:
                mock_reset.return_value = {
                    "success": True,
                    "message": "Password reset email sent successfully"
                }
                
                response = client.post(
                    "/api/v1/users/reset-password",
                    json={"phone_number": "+1234567890"},
                    headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "password reset email sent" in data["message"].lower()
                
                # Verify the services were called with correct parameters
                mock_get_email.assert_called_once_with(ANY, "+1234567890")
                mock_reset.assert_called_once_with("test@example.com")

    def test_reset_password_phone_not_found(self, client: TestClient, mock_session):
        """Test password reset when phone number is not found."""
        
        # Mock UserService.get_email_by_phone to return None
        with patch('src.services.users.UserService.get_email_by_phone') as mock_get_email:
            mock_get_email.return_value = None
            
            response = client.post(
                "/api/v1/users/reset-password",
                json={"phone_number": "+1234567890"},
                headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"}
            )
            
            assert response.status_code == 404
            data = response.json()
            assert "no account found" in data["detail"].lower()

    def test_reset_password_invalid_phone(self, client: TestClient):
        """Test password reset with invalid phone number."""
        
        response = client.post(
            "/api/v1/users/reset-password",
            json={"phone_number": "invalid-phone"},
            headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"}
        )
        
        assert response.status_code == 422  # Validation error

    def test_reset_password_auth_service_failure(self, client: TestClient, mock_session):
        """Test password reset when AuthService fails."""
        
        # Mock UserService.get_email_by_phone to return an email
        with patch('src.services.users.UserService.get_email_by_phone') as mock_get_email:
            mock_get_email.return_value = "test@example.com"
            
            # Mock AuthService.reset_password to return failure
            with patch('src.services.auth.AuthService.reset_password') as mock_reset:
                mock_reset.return_value = {
                    "success": False,
                    "message": "Failed to send reset email"
                }
                
                response = client.post(
                    "/api/v1/users/reset-password",
                    json={"phone_number": "+1234567890"},
                    headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"}
                )
                
                assert response.status_code == 400
                data = response.json()
                assert "failed to send reset email" in data["detail"].lower()
