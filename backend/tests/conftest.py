"""
Test configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool
from unittest.mock import Mock, patch
import tempfile
import os

# Import the app and dependencies
from src.app import app
from src.db.session import get_session
from src.services.supabase_client import supabase


# Create test database engine
@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Import models to create tables
    from src.models.user import User, Driver, Rider, Admin
    from sqlmodel import SQLModel
    
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with dependency overrides."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    
    # Set test API key in environment (use the same key from .env)
    os.environ["TAXINI_API_KEY"] = "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
    
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing with updated response format."""
    with patch('src.services.supabase_client.supabase') as mock_client, \
         patch('src.services.supabase_client.ensure_supabase_client') as mock_ensure:
        
        # Make ensure_supabase_client return our mock
        mock_ensure.return_value = mock_client
        
        # Mock auth responses in dict format (current supabase-py style)
        mock_client.auth.sign_in_with_otp.return_value = {
            "data": {"session": None, "user": None},
            "error": None
        }
        
        mock_client.auth.verify_otp.return_value = {
            "data": {
                "session": {
                    "access_token": "test_access_token",
                    "refresh_token": "test_refresh_token",
                    "expires_in": 3600
                },
                "user": {
                    "id": "test_user_id",
                    "phone": "+1234567890",
                    "email": "test@example.com",
                    "email_confirmed_at": "2024-01-01T00:00:00Z",
                    "phone_confirmed_at": "2024-01-01T00:00:00Z"
                }
            },
            "error": None
        }
        
        mock_client.auth.get_user.return_value = {
            "data": {
                "user": {
                    "id": "test_user_id",
                    "phone": "+1234567890",
                    "email": "test@example.com",
                    "email_confirmed_at": "2024-01-01T00:00:00Z",
                    "phone_confirmed_at": "2024-01-01T00:00:00Z"
                }
            },
            "error": None
        }
        
        mock_client.auth.refresh_session.return_value = {
            "data": {
                "session": {
                    "access_token": "new_test_access_token",
                    "refresh_token": "new_test_refresh_token",
                    "expires_in": 3600
                }
            },
            "error": None
        }
        
        # Mock storage responses
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.upload.return_value = {"error": None}
        mock_bucket.get_public_url.return_value = "https://example.com/test-file.jpg"
        mock_storage.from_.return_value = mock_bucket
        mock_client.storage = mock_storage
        
        yield mock_client


@pytest.fixture
def sample_image_file():
    """Create a sample image file for testing uploads."""
    # Create a small test image file
    content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\x0f\x01P\x01\x00\x00\x00\x00IEND\xaeB`\x82'
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        yield tmp.name
    
    # Cleanup
    os.unlink(tmp.name)


@pytest.fixture
def valid_auth_headers(mock_supabase):
    """Provide valid authorization headers for testing."""
    return {
        "Authorization": "Bearer test_access_token",
        "X-API-Key": "Tw_82EVzdQY9pWSaNbN29MyxFCDESSRlcndy9SHwQnw"
    }


@pytest.fixture
def driver_profile_data():
    """Sample driver profile data for testing."""
    return {
        "name": "John Driver",
        "email": "john@example.com",
        "role": "driver",
        "taxi_number": "TAXI-123",
        "account_status": "locked"
    }


@pytest.fixture
def rider_profile_data():
    """Sample rider profile data for testing."""
    return {
        "name": "Jane Rider",
        "email": "jane@example.com",
        "role": "rider",
        "residence_place": "Downtown"
    }
