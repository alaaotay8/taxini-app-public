"""
Tests for authentication service and endpoints.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from src.services.auth import AuthService


class TestAuthService:
    """Test cases for AuthService class."""

    def test_send_otp_success(self, mock_supabase):
        """Test successful OTP sending."""
        phone_number = "+1234567890"
        
        result = AuthService.send_otp(phone_number)
        
        assert result["success"] is True
        assert "OTP sent successfully" in result["message"]
        mock_supabase.auth.sign_in_with_otp.assert_called_once()

    def test_send_otp_failure(self, mock_supabase):
        """Test OTP sending failure."""
        phone_number = "+1234567890"
        mock_supabase.auth.sign_in_with_otp.return_value = {
            "data": None,
            "error": {"message": "Invalid phone number"}
        }
        
        result = AuthService.send_otp(phone_number)
        
        assert result["success"] is False
        assert "Invalid phone number" in result["message"]

    def test_verify_otp_success(self, mock_supabase):
        """Test successful OTP verification."""
        phone_number = "+1234567890"
        otp_code = "123456"
        
        result = AuthService.verify_otp(phone_number, otp_code)
        
        assert result["success"] is True
        assert "Phone number verified successfully" == result["message"]
        assert "session" in result  # Updated to match new response format
        assert "user" in result
        mock_supabase.auth.verify_otp.assert_called_once()

    def test_verify_otp_failure(self, mock_supabase):
        """Test OTP verification failure."""
        phone_number = "+1234567890"
        otp_code = "wrong_otp"
        mock_supabase.auth.verify_otp.return_value = {
            "data": None,
            "error": {"message": "Invalid OTP"}
        }
        
        result = AuthService.verify_otp(phone_number, otp_code)
        
        assert result["success"] is False
        assert "Invalid OTP" in result["message"]

    def test_get_user_by_token_success(self, mock_supabase):
        """Test successful user retrieval by token."""
        access_token = "valid_token"
        
        result = AuthService.get_user_by_token(access_token)
        
        assert result["success"] is True
        assert "user" in result
        assert result["user"]["id"] == "test_user_id"
        mock_supabase.auth.get_user.assert_called_once_with(access_token)

    def test_get_user_by_token_failure(self, mock_supabase):
        """Test user retrieval failure with invalid token."""
        access_token = "invalid_token"
        mock_supabase.auth.get_user.return_value = {
            "data": None,
            "error": {"message": "Invalid token"}
        }
        
        result = AuthService.get_user_by_token(access_token)
        
        assert result["success"] is False
        assert "Invalid token" in result["message"]


class TestAuthEndpoints:
    """Test cases for authentication endpoints."""

    def test_send_otp_endpoint_success(self, client: TestClient, mock_supabase):
        """Test /send-otp endpoint success."""
        response = client.post(
            "/api/v1/auth/send-otp",
            json={"phone_number": "+1234567890"},
            headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "OTP sent successfully" in data["message"]

    def test_send_otp_endpoint_invalid_phone(self, client: TestClient):
        """Test /send-otp endpoint with invalid phone number."""
        response = client.post(
            "/api/v1/auth/send-otp",
            json={"phone_number": "invalid_phone"},
            headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"}
        )
        
        assert response.status_code == 400  # Bad request for invalid input

    def test_verify_otp_endpoint_success(self, client: TestClient, mock_supabase):
        """Test /verify-otp endpoint success."""
        response = client.post(
            "/api/v1/auth/verify-otp",
            json={"phone_number": "+1234567890", "otp_code": "123456"},
            headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "session" in data
        assert "access_token" in data["session"]
        assert "refresh_token" in data["session"]

    def test_auth_me_endpoint_success(self, client: TestClient, mock_supabase):
        """Test /auth/me endpoint with valid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": "Bearer test_access_token",
                "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "user" in data

    def test_auth_me_endpoint_no_token(self, client: TestClient):
        """Test /auth/me endpoint without token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"}
        )
        
        assert response.status_code == 401

    def test_auth_me_endpoint_invalid_token(self, client: TestClient, mock_supabase):
        """Test /auth/me endpoint with invalid token."""
        mock_supabase.auth.get_user.return_value = {
            "data": None,
            "error": {"message": "Invalid token"}
        }
        
        response = client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": "Bearer invalid_token",
                "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
            }
        )
        
        assert response.status_code == 401
