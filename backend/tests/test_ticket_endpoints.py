"""
Tests for ticket API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime, timedelta
import jwt

from src.models.user import User
from src.models.ticket import Ticket, TicketStatus, TicketPriority
from src.models.enums import UserRole
from src.core.settings import settings


class TestTicketEndpoints:
    """Test cases for ticket API endpoints."""
    
    @pytest.fixture
    def test_user(self, session: Session):
        """Create a test user."""
        user = User(
            id="test_user_id",
            name="Test User",
            email="test@example.com",
            phone_number="+1234567890",
            role=UserRole.RIDER,
            auth_id="test_auth_id",
            auth_status="verified"
        )
        session.add(user)
        session.commit()
        return user
    
    @pytest.fixture
    def test_admin(self, session: Session):
        """Create a test admin user."""
        admin_user = User(
            id="test_admin_id",
            name="Admin User",
            email="admin@example.com",
            phone_number="+9876543210",
            role=UserRole.ADMIN,
            auth_id="admin_auth_id",
            auth_status="verified"
        )
        session.add(admin_user)
        
        # Create admin profile
        from src.models.user import Admin
        admin_profile = Admin(
            id="test_admin_profile_id",
            user_id=admin_user.id
        )
        session.add(admin_profile)
        session.commit()
        return admin_user
    
    @pytest.fixture
    def test_ticket(self, session: Session, test_user):
        """Create a test ticket."""
        ticket = Ticket(
            id="test_ticket_id",
            title="Test Ticket",
            content="This is a test ticket content",
            user_id=test_user.id,
            user_role=test_user.role,
            status=TicketStatus.OPEN,
            priority=TicketPriority.MEDIUM,
            created_at=datetime.utcnow()
        )
        session.add(ticket)
        session.commit()
        return ticket
    
    @pytest.fixture
    def user_token(self, test_user):
        """Create a JWT token for a user."""
        payload = {
            "sub": test_user.auth_id,
            "email": test_user.email,
            "role": test_user.role,
            "user_id": test_user.id,
            "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
        }
        token = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )
        return token
    
    @pytest.fixture
    def admin_token(self, test_admin):
        """Create a JWT token for an admin."""
        payload = {
            "sub": test_admin.auth_id,
            "email": test_admin.email,
            "role": UserRole.ADMIN.value,
            "user_id": test_admin.id,
            "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
        }
        token = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )
        return token

    def test_create_ticket_success(self, client: TestClient, user_token):
        """Test successful ticket creation."""
        response = client.post(
            "/api/v1/tickets",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "title": "New Ticket",
                "content": "This is a new ticket",
                "priority": "high"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Ticket"
        assert data["content"] == "This is a new ticket"
        assert data["priority"] == "high"
        assert data["status"] == "open"
    
    def test_create_ticket_validation_error(self, client: TestClient, user_token):
        """Test ticket creation with invalid data."""
        response = client.post(
            "/api/v1/tickets",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "title": "Hi",  # Too short
                "content": "Short",  # Too short
                "priority": "invalid"  # Invalid enum value
            }
        )
        
        assert response.status_code == 422
    
    def test_get_user_tickets(self, client: TestClient, user_token, test_ticket):
        """Test getting a user's tickets."""
        response = client.get(
            "/api/v1/tickets",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        assert len(data["tickets"]) == 1
        assert data["tickets"][0]["id"] == test_ticket.id
    
    def test_get_ticket_by_id(self, client: TestClient, user_token, test_ticket):
        """Test getting a specific ticket by ID."""
        response = client.get(
            f"/api/v1/tickets/{test_ticket.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_ticket.id
        assert data["title"] == test_ticket.title
    
    def test_get_nonexistent_ticket(self, client: TestClient, user_token):
        """Test getting a ticket that doesn't exist."""
        response = client.get(
            "/api/v1/tickets/nonexistent_id",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 404
    
    def test_update_ticket(self, client: TestClient, user_token, test_ticket):
        """Test updating a ticket."""
        response = client.patch(
            f"/api/v1/tickets/{test_ticket.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "title": "Updated Ticket",
                "priority": "high"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Ticket"
        assert data["priority"] == "high"
        assert data["content"] == test_ticket.content  # Unchanged
    
    def test_admin_list_all_tickets(self, client: TestClient, admin_token, test_ticket):
        """Test admin listing all tickets."""
        response = client.get(
            "/api/v1/admin/tickets",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        assert len(data["tickets"]) == 1
        assert data["tickets"][0]["id"] == test_ticket.id
        # Check for admin-specific fields
        assert "user_name" in data["tickets"][0]
        assert "user_email" in data["tickets"][0]
    
    def test_admin_get_ticket_stats(self, client: TestClient, admin_token, test_ticket):
        """Test getting ticket statistics as admin."""
        response = client.get(
            "/api/v1/admin/tickets/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert data["total"] >= 1
        assert "open" in data
        assert data["open"] >= 1
    
    def test_admin_get_specific_ticket(self, client: TestClient, admin_token, test_ticket):
        """Test admin getting a specific ticket."""
        response = client.get(
            f"/api/v1/admin/tickets/{test_ticket.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_ticket.id
        # Check for admin-specific fields
        assert "user_name" in data
        assert "user_email" in data
    
    def test_admin_update_ticket(self, client: TestClient, admin_token, test_ticket):
        """Test admin updating a ticket."""
        response = client.patch(
            f"/api/v1/admin/tickets/{test_ticket.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "status": "in_progress",
                "admin_notes": "Working on this"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["admin_notes"] == "Working on this"
    
    def test_user_cannot_access_admin_endpoints(self, client: TestClient, user_token):
        """Test that regular users can't access admin endpoints."""
        response = client.get(
            "/api/v1/admin/tickets",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
    
    def test_unauthorized_access(self, client: TestClient):
        """Test access without authentication."""
        response = client.get("/api/v1/tickets")
        
        assert response.status_code == 401
