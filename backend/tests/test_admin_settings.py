"""
Tests for admin settings management endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.models.user import User, Admin
from src.models.settings import Settings
from src.services.admin_auth import AdminAuthService


class TestAdminSettings:
    """Test class for admin settings management functionality."""

    @pytest.fixture
    def admin_token(self, session: Session):
        """Create admin user and get authentication token."""
        # Create admin user
        admin_user = User(
            auth_id="admin-settings-test",
            name="Settings Admin",
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
            test_column="settings_admin"
        )
        session.add(admin_profile)
        session.commit()
        
        # Generate token
        auth_service = AdminAuthService()
        token = auth_service.create_admin_token(admin_user.id, admin_user.email)
        return token

    @pytest.fixture
    def sample_settings(self, session: Session):
        """Create sample settings for testing."""
        settings_data = [
            {
                "setting_key": "approach_fee_rate_per_km",
                "setting_value": "0.5",
                "data_type": "float",
                "description": "Fee rate per kilometer for driver approach to pickup location (TND/km)",
                "category": "pricing",
                "is_active": True,
                "is_editable": True
            },
            {
                "setting_key": "base_fare",
                "setting_value": "2.0",
                "data_type": "float",
                "description": "Base fare for all trips (TND)",
                "category": "pricing",
                "is_active": True,
                "is_editable": True
            },
            {
                "setting_key": "commission_rate",
                "setting_value": "0.15",
                "data_type": "float",
                "description": "Platform commission rate (decimal, e.g., 0.15 = 15%)",
                "category": "pricing",
                "is_active": True,
                "is_editable": True
            },
            {
                "setting_key": "system_version",
                "setting_value": "1.0.0",
                "data_type": "string",
                "description": "Current system version",
                "category": "system",
                "is_active": True,
                "is_editable": False  # Read-only setting
            }
        ]
        
        created_settings = []
        for setting_data in settings_data:
            setting = Settings(**setting_data)
            session.add(setting)
            created_settings.append(setting)
        
        session.commit()
        return created_settings

    def test_get_all_settings_success(self, client: TestClient, admin_token: str, sample_settings):
        """Test successful retrieval of all settings."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        response = client.get("/api/v1/admin/settings", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["data"]) >= 4
        
        # Check that all required fields are present
        setting = data["data"][0]
        required_fields = [
            "id", "setting_key", "setting_value", "data_type",
            "description", "category", "is_active", "is_editable"
        ]
        for field in required_fields:
            assert field in setting

    def test_get_settings_by_category(self, client: TestClient, admin_token: str, sample_settings):
        """Test filtering settings by category."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        response = client.get("/api/v1/admin/settings?category=pricing", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        # Should only return pricing settings
        for setting in data["data"]:
            assert setting["category"] == "pricing"

    def test_get_specific_setting_success(self, client: TestClient, admin_token: str, sample_settings):
        """Test successful retrieval of a specific setting."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        response = client.get("/api/v1/admin/settings/approach_fee_rate_per_km", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        setting = data["data"]
        assert setting["setting_key"] == "approach_fee_rate_per_km"
        assert setting["setting_value"] == "0.5"
        assert setting["data_type"] == "float"

    def test_get_setting_not_found(self, client: TestClient, admin_token: str):
        """Test retrieval of non-existent setting."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        response = client.get("/api/v1/admin/settings/non_existent_setting", headers=headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_approach_fee_rate_success(self, client: TestClient, admin_token: str, sample_settings, session: Session):
        """Test successful update of approach fee rate."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw",
            "Content-Type": "application/json"
        }
        
        update_data = {
            "setting_value": "0.7",
            "description": "Updated approach fee rate for better driver compensation"
        }
        
        response = client.put(
            "/api/v1/admin/settings/approach_fee_rate_per_km",
            headers=headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "updated successfully" in data["message"]
        
        updated_setting = data["data"]
        assert updated_setting["setting_value"] == "0.7"
        assert updated_setting["description"] == update_data["description"]
        assert updated_setting["updated_at"] is not None
        
        # Verify in database
        db_setting = session.exec(
            select(Settings).where(Settings.setting_key == "approach_fee_rate_per_km")
        ).first()
        assert db_setting.setting_value == "0.7"

    def test_update_base_fare_success(self, client: TestClient, admin_token: str, sample_settings):
        """Test successful update of base fare."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw",
            "Content-Type": "application/json"
        }
        
        update_data = {"setting_value": "2.5"}
        
        response = client.put(
            "/api/v1/admin/settings/base_fare",
            headers=headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["setting_value"] == "2.5"

    def test_update_commission_rate_success(self, client: TestClient, admin_token: str, sample_settings):
        """Test successful update of commission rate."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw",
            "Content-Type": "application/json"
        }
        
        update_data = {
            "setting_value": "0.20",
            "description": "Increased commission rate to 20%"
        }
        
        response = client.put(
            "/api/v1/admin/settings/commission_rate",
            headers=headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["setting_value"] == "0.20"

    def test_update_readonly_setting_fails(self, client: TestClient, admin_token: str, sample_settings):
        """Test that updating a read-only setting fails."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw",
            "Content-Type": "application/json"
        }
        
        update_data = {"setting_value": "2.0.0"}
        
        response = client.put(
            "/api/v1/admin/settings/system_version",
            headers=headers,
            json=update_data
        )
        
        assert response.status_code == 400
        assert "not editable" in response.json()["detail"]

    def test_update_setting_not_found(self, client: TestClient, admin_token: str):
        """Test updating non-existent setting."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw",
            "Content-Type": "application/json"
        }
        
        update_data = {"setting_value": "1.0"}
        
        response = client.put(
            "/api/v1/admin/settings/non_existent_setting",
            headers=headers,
            json=update_data
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_setting_invalid_value_type(self, client: TestClient, admin_token: str, sample_settings):
        """Test updating setting with invalid value type."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw",
            "Content-Type": "application/json"
        }
        
        # Try to set non-numeric value for float setting
        update_data = {"setting_value": "invalid_number"}
        
        response = client.put(
            "/api/v1/admin/settings/approach_fee_rate_per_km",
            headers=headers,
            json=update_data
        )
        
        assert response.status_code == 400
        assert "Invalid value" in response.json()["detail"]

    def test_update_setting_missing_value(self, client: TestClient, admin_token: str):
        """Test updating setting without providing value."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw",
            "Content-Type": "application/json"
        }
        
        response = client.put(
            "/api/v1/admin/settings/approach_fee_rate_per_km",
            headers=headers,
            json={}
        )
        
        assert response.status_code == 422  # Validation error

    def test_settings_unauthorized(self, client: TestClient):
        """Test settings endpoints without authentication."""
        # Test GET
        response = client.get("/api/v1/admin/settings")
        assert response.status_code == 401
        
        # Test PUT
        response = client.put(
            "/api/v1/admin/settings/approach_fee_rate_per_km",
            json={"setting_value": "0.8"}
        )
        assert response.status_code == 401

    def test_settings_invalid_token(self, client: TestClient):
        """Test settings endpoints with invalid token."""
        headers = {
            "Authorization": "Bearer invalid_token",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        response = client.get("/api/v1/admin/settings", headers=headers)
        assert response.status_code == 401

    def test_settings_missing_api_key(self, client: TestClient, admin_token: str):
        """Test settings endpoints without API key."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.get("/api/v1/admin/settings", headers=headers)
        assert response.status_code == 401

    def test_settings_response_structure(self, client: TestClient, admin_token: str, sample_settings):
        """Test that settings responses have correct structure."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        # Test GET all settings
        response = client.get("/api/v1/admin/settings", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert isinstance(data["data"], list)
        
        # Test GET specific setting
        response = client.get("/api/v1/admin/settings/base_fare", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert isinstance(data["data"], dict)

    def test_settings_value_type_conversion(self, client: TestClient, admin_token: str, sample_settings):
        """Test that setting values are properly converted based on data type."""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
        }
        
        # Test float conversion
        response = client.get("/api/v1/admin/settings/approach_fee_rate_per_km", headers=headers)
        assert response.status_code == 200
        
        setting = response.json()["data"]
        assert setting["data_type"] == "float"
        # Value should be stored as string but convertible to float
        assert float(setting["setting_value"]) == 0.5
